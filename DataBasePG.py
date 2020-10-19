import datetime

import psycopg2
from psycopg2 import Error
from abc import ABC
from Utils import Utils
from models.Models import Pars


class DataBaseStandart(ABC):
    CONN = None
    CREATE_TABLE = 'CREATE TABLE'
    CREATE_SEQUENCE = 'CREATE SEQUENCE'
    INT = 'INTEGER'
    TEXT = 'TEXT'
    BOOL = 'BOOLEAN'
    DATE = 'DATE'
    DATETIME = 'DATETIME'
    NOT_NULL = 'NOT NULL'
    PK = 'PRIMARY KEY'
    FK = 'FOREIGN KEY'
    REFERENCES = 'REFERENCES'
    AUTOINCREMENT = 'AUTOINCREMENT'
    DEFAULT = 'DEFAULT'

    @classmethod
    def create_tables(cls):
        pass


class DataBasePg(DataBaseStandart):
    def get_stat(self, date_from=None, date_to=None):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        if date_to is None and date_from is None:
            c.execute('SELECT st_requests, st_date FROM STATICS')
        else:
            c.execute('SELECT st_requests, st_date FROM STATICS WHERE date(st_date) >= date(%s) and date(st_date) <= date(%s)', (date_from, date_to))
        result = c.fetchall()
        c.close()
        self.conn_open_close(0)
        return result

    def insert_stat(self, date):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        c.execute('SELECT st_requests FROM STATICS where st_date = %s', (date,))
        res = c.fetchone()
        if res is None:
            c.execute('INSERT INTO STATICS (st_requests, st_date) VALUES (%s, %s)', (1, date))
        else:
            c.execute('UPDATE STATICS SET st_requests = %s WHERE st_date = %s', (res[0]+1, date))
        self.CONN.commit()
        c.close()
        self.conn_open_close(0)

    def update_message_id(self, message_id, tg_id):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        c.execute('UPDATE USERS SET message_id = %s where tg_id = %s', (message_id, tg_id))
        self.CONN.commit()
        c.close()
        self.conn_open_close(0)

    def delete_timetables_date(self, date):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        for date in date:
            c.execute('DELETE FROM TIMETABLES where date_lesson = %s', (date,))
        self.CONN.commit()
        c.close()
        self.conn_open_close(0)

    def insert_timetables(self, par):
        self.conn_open_close(1)
        c = self.CONN.cursor()

        c.execute('SELECT id FROM LESSONS where name = %s', (par.lesson,))
        id_lesson = c.fetchone()
        if id_lesson is None:
            c.execute('INSERT INTO LESSONS (name) VALUES (%s)', (par.lesson,))
            c.execute('SELECT id FROM LESSONS where name = %s', (par.lesson,))
            id_lesson = c.fetchone()[0]
        else:
            id_lesson = id_lesson[0]

        c.execute('SELECT id FROM TEACHERS where name = %s', (par.teacher,))
        id_teacher = c.fetchone()
        if id_teacher is None:
            c.execute('INSERT INTO TEACHERS (name) VALUES (%s)', (par.teacher,))
            c.execute('SELECT id FROM TEACHERS where name = %s', (par.teacher,))
            id_teacher = c.fetchone()[0]
        else:
            id_teacher = id_teacher[0]

        c.execute('SELECT id FROM TIMES where time = %s', (par.time,))
        id_time = c.fetchone()
        if id_time is None:
            c.execute('INSERT INTO TIMES (time) VALUES (%s)', (par.time,))
            c.execute('SELECT id FROM TIMES where time = %s', (par.time,))
            id_time = c.fetchone()[0]
        else:
            id_time = id_time[0]

        c.execute('SELECT id FROM GROUPS where name = %s', (par.group,))
        id_group = c.fetchone()[0]
        self.CONN.commit()

        c.execute('INSERT INTO TIMETABLES (id_lesson, id_teacher, id_time, id_classroom, id_group, date_lesson)' +
                  'values (%s,%s,%s,%s,%s,%s)', (id_lesson, id_teacher, id_time, 1, id_group, par.date_lesson))
        self.CONN.commit()
        c.close()
        self.conn_open_close(0)

    def get_all_info_about_user(self, tg_id):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        c.execute(
            'SELECT s.tg_id, s.tg_username, s.is_admin, g.name FROM USERS s, GROUPS g WHERE s.id_group=g.id and s.tg_id = %s',
            (tg_id,))
        result = c.fetchone()
        c.close()
        self.conn_open_close(0)
        return result

    def get_all_groups(self):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        c.execute('SELECT name FROM GROUPS')
        result = c.fetchall()
        c.close()
        self.conn_open_close(0)
        return result

    def set_group_and_tg_id_user(self, group, username, tg_id):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        c.execute('SELECT id FROM GROUPS WHERE name = %s', (group,))
        id_group = c.fetchone()[0]
        c.execute('SELECT tg_id FROM USERS WHERE tg_id = %s', (tg_id,))
        is_tg_id = c.fetchone()
        if is_tg_id is None:
            c.execute('UPDATE USERS set id_group = %s, tg_id = %s where tg_username = %s', (id_group, tg_id, username))
        elif is_tg_id is not None and username != '':
            c.execute('UPDATE USERS set id_group = %s, tg_username = %s where tg_id = %s', (id_group, username, tg_id))
        else:
            c.execute('UPDATE USERS set id_group = %s where tg_id = %s', (id_group, tg_id))
        self.CONN.commit()
        c.close()
        self.conn_open_close(0)

    def insert_users(self, username, is_admin=0, is_only_tgid=None, id_group=None):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        if is_only_tgid and is_only_tgid is not None:
            name = 'Group ' + str(datetime.datetime.now())
            c.execute('INSERT INTO USERS (tg_id, is_admin, id_group, tg_username) VALUES (%s, %s, %s, %s)', (username,
                                                                                                             is_admin,
                                                                                                             id_group,
                                                                                                             name))
        elif not is_only_tgid and is_only_tgid is not None:
            name = 'User ' + str(datetime.datetime.now())
            c.execute('INSERT INTO USERS (tg_id, is_admin, id_group, tg_username) VALUES (%s, %s, %s, %s)', (username,
                                                                                                             is_admin,
                                                                                                             id_group,
                                                                                                             name))
        else:
            c.execute('INSERT INTO USERS (tg_username, is_admin) VALUES (%s, %s)', (username, is_admin))
        self.CONN.commit()
        c.close()
        self.conn_open_close(0)

    def get_next_date(self, flag, date):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        result = ''

        if flag == '1':
            c.execute(
                'SELECT DISTINCT date_lesson FROM TIMETABLES where date(date_lesson) > date(%s) order by date_lesson',
                (date,))
            result = c.fetchone()
        elif flag == '0':
            c.execute(
                'SELECT DISTINCT date_lesson FROM TIMETABLES where date(date_lesson) < date(%s) order by date_lesson desc',
                (date,))
            result = c.fetchone()
        c.close()
        self.conn_open_close(0)

        if result is None:
            return None

        return result[0]

    def get_timetable_dates(self):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        c.execute('SELECT DISTINCT date_lesson FROM TIMETABLES')
        result = c.fetchall()
        c.close()
        self.conn_open_close(0)
        return result

    def get_timetable(self, tg_id, date=None):
        self.conn_open_close(1)
        c = self.CONN.cursor()

        c.execute('SELECT id_group FROM USERS where tg_id = %s', (tg_id,))
        id_group = c.fetchone()[0]

        if date is None:
            date = Utils.get_date_now()

            i = 1
            while True:
                if i == 30:
                    return None
                c.execute('SELECT id FROM TIMETABLES where date_lesson = %s and id_group = %s',
                          (date, id_group))
                res = c.fetchone()
                if res is None:
                    date = Utils.get_date_now(i)
                    i += 1
                else:
                    break

        c.execute(
            'SELECT s.date_lesson, l.name, t.name, ts.time, g.name FROM TIMETABLES s, TIMES ts, TEACHERS t, LESSONS l, GROUPS g WHERE s.id_group = g.id and s.date_lesson = %s and s.id_group = %s and ts.id = s.id_time and t.id = s.id_teacher and l.id = s.id_lesson ORDER BY s.id',
            (date, id_group))
        result = c.fetchall()
        c.close()
        self.conn_open_close(0)

        data_pars = []
        for par in result:
            data_pars.append(Pars(par[0], par[1], par[4], par[3], par[2]))
        return data_pars

    def get_timetables(self, date, group):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        c.execute('SELECT id FROM GROUPS where name = %s', (group,))
        id_group = c.fetchone()[0]
        c.execute(
            'SELECT s.date_lesson, l.name, t.name, ts.time FROM TIMETABLES s, TIMES ts, TEACHERS t, LESSONS l WHERE s.date_lesson = %s and s.id_group = %s and ts.id = s.id_time and t.id = s.id_teacher and l.id = s.id_lesson',
            (date, id_group))
        result = c.fetchall()
        c.close()
        self.conn_open_close(0)

        data_pars = []
        for par in result:
            data_pars.append(Pars(par[0], par[1], group, par[3], par[2]))
        return data_pars

    def is_admin(self, tg_id):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        c.execute('SELECT is_admin FROM USERS WHERE tg_id = %s', (tg_id,))
        result = c.fetchone()[0]
        c.close()
        self.conn_open_close(0)
        return result

    def is_user(self, tg_id=None, username=None):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        result = None
        if tg_id is not None:
            c.execute('SELECT TG_ID FROM USERS WHERE TG_ID = %s', (tg_id,))
            result = c.fetchone()
        elif username is not None:
            c.execute('SELECT TG_ID FROM USERS WHERE tg_username = %s', (username,))
            result = c.fetchone()
        c.close()
        self.conn_open_close(0)
        if result is not None:
            return True
        return False

    def get_all_user(self):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        c.execute('SELECT tg_id FROM USERS WHERE tg_id is not null')
        result = c.fetchall()
        c.close()
        self.conn_open_close(0)
        return result

    def get_all_corp(self):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        c.execute('SELECT body FROM CORPS')
        result = c.fetchall()
        c.close()
        self.conn_open_close(0)
        return result

    def insert_init(self):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        try:
            """"
            c.execute("INSERT INTO CORPS (body) VALUES ('1 корпус - ул. Студенческая, 38')")
            c.execute("INSERT INTO CORPS (body) VALUES ('2 корпус - бульвар Гагарина, 37')")
            c.execute("INSERT INTO CORPS (body) VALUES ('3 корпус - бульвар Гагарина, 37а')")
            c.execute("INSERT INTO CORPS (body) VALUES ('4 корпус - ул. Лебедева, 27')")
            c.execute("INSERT INTO CORPS (body) VALUES ('5 корпус - ул. Студенческая, 23')")
            c.execute("INSERT INTO TIMES (time) VALUES ('09:10-10:30')")
            c.execute("INSERT INTO TIMES (time) VALUES ('10:40-12:00')")
            c.execute("INSERT INTO TIMES (time) VALUES ('12:40-14:00')")
            c.execute("INSERT INTO TIMES (time) VALUES ('14:10-15:30')")
            c.execute("INSERT INTO TIMES (time) VALUES ('15:40-17:00')")
            c.execute("INSERT INTO TIMES (time) VALUES ('17:10-18:30')")
            c.execute("INSERT INTO TIMES (time) VALUES ('18:40-20:00')")
            c.execute("INSERT INTO TIMES (time) VALUES ('20:10-21:30')")
            c.execute("INSERT INTO GROUPS (name) VALUES ('ПИ-20СВ-1(16)')")
            c.execute("INSERT INTO GROUPS (name) VALUES ('ПИ-20СВ-2 (15)')")
            self.CONN.commit()
            """
        except Error as e:
            pass

        c.close()
        self.conn_open_close(0)

    def conn_open_close(self, stat):
        if stat == 1:
            self.CONN = psycopg2.connect(dbname='HSE', user='hse_users', password='hse_users_password',
                                         host='localhost')
        else:
            self.CONN.close()

    def create_tables(self):
        try:
            self.conn_open_close(1)
            c = self.CONN.cursor()
            c.execute(f'{self.CREATE_TABLE} STATICS (id SERIAL {self.PK}, st_requests {self.INT}, st_date {self.TEXT})')
            c.execute(f'{self.CREATE_TABLE} CORPS (id SERIAL {self.PK}, body {self.TEXT})')
            c.execute(f'{self.CREATE_TABLE} TIMES (id SERIAL {self.PK}, time {self.TEXT})')
            c.execute(f'{self.CREATE_TABLE} CLASSROOMS (id SERIAL {self.PK}, name {self.TEXT})')
            c.execute(f'{self.CREATE_TABLE} TEACHERS (id SERIAL {self.PK}, name {self.TEXT})')
            c.execute(f'{self.CREATE_TABLE} LESSONS (id SERIAL {self.PK}, name {self.TEXT})')
            c.execute(f'{self.CREATE_TABLE} GROUPS (id SERIAL {self.PK}, name {self.TEXT})')
            c.execute(f'{self.CREATE_TABLE} TIMETABLES (id SERIAL {self.PK}, '
                      f'id_lesson {self.INT} {self.NOT_NULL}, '
                      f'id_teacher {self.INT} {self.NOT_NULL}, '
                      f'id_time {self.INT} {self.NOT_NULL}, '
                      f'id_classroom {self.INT} {self.NOT_NULL}, '
                      f'id_group {self.INT} {self.NOT_NULL}, '
                      f'date_lesson {self.TEXT} {self.NOT_NULL}, '
                      f'{self.FK} (id_lesson) {self.REFERENCES} LESSONS (id), '
                      f'{self.FK} (id_teacher) {self.REFERENCES} TEACHERS (id), '
                      f'{self.FK} (id_time) {self.REFERENCES} TIMES (id), '
                      f'{self.FK} (id_classroom) {self.REFERENCES} CLASSROOMS (id),'
                      f'{self.FK} (id_group) {self.REFERENCES} GROUPS (id))')
            c.execute(f'{self.CREATE_TABLE} USERS (tg_id BIGINT, tg_username {self.TEXT} {self.PK}, '
                      f'is_admin {self.INT}, id_group {self.INT}, message_id {self.TEXT},'
                      f'{self.FK} (id_group) {self.REFERENCES} GROUPS (id))')
            #c.execute(f'{self.CREATE_TABLE} subscriptions (tg_id {self.INT}, time {self.TEXT},)')
            self.CONN.commit()
            c.close()
            self.conn_open_close(0)
        except Error as e:
            pass

    def __init__(self):
        self.create_tables()
        self.insert_init()
