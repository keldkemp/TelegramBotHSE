import sqlite3
from sqlite3 import Error
from abc import ABC
from Utils.Utils import Utils
from models.Models import Pars


class DataBaseStandart(ABC):
    CONN = None
    CREATE_TABLE = 'CREATE TABLE'
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


class DataBase(DataBaseStandart):
    DBFILE = 'sqlitedb.db'

    def update_message_id(self, message_id, tg_id):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        c.execute('UPDATE USERS SET message_id = ? where tg_id = ?', (message_id, tg_id))
        self.CONN.commit()
        c.close()
        self.conn_open_close(0)

    def delete_timetables_date(self, date):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        for date in date:
            c.execute('DELETE FROM TIMETABLES where date_lesson = ?', (date,))
        self.CONN.commit()
        c.close()
        self.conn_open_close(0)

    def insert_timetables(self, par):
        self.conn_open_close(1)
        c = self.CONN.cursor()

        id_lesson = c.execute('SELECT id FROM LESSONS where name = ?', (par.lesson,)).fetchone()
        if id_lesson is None:
            c.execute('INSERT INTO LESSONS (name) VALUES (?)', (par.lesson, ))
            id_lesson = c.execute('SELECT id FROM LESSONS where name = ?', (par.lesson,)).fetchone()[0]
        else:
            id_lesson = id_lesson[0]

        id_teacher = c.execute('SELECT id FROM TEACHERS where name = ?', (par.teacher,)).fetchone()
        if id_teacher is None:
            c.execute('INSERT INTO TEACHERS (name) VALUES (?)', (par.teacher, ))
            id_teacher = c.execute('SELECT id FROM TEACHERS where name = ?', (par.teacher,)).fetchone()[0]
        else:
            id_teacher = id_teacher[0]

        id_time = c.execute('SELECT id FROM TIMES where time = ?', (par.time,)).fetchone()
        if id_time is None:
            c.execute('INSERT INTO TIMES (time) VALUES (?)', (par.time,))
            id_time = c.execute('SELECT id FROM TIMES where time = ?', (par.time,)).fetchone()[0]
        else:
            id_time = id_time[0]

        id_group = c.execute('SELECT id FROM GROUPS where name = ?', (par.group,)).fetchone()[0]

        c.execute('INSERT INTO TIMETABLES (id_lesson, id_teacher, id_time, id_classroom, id_group, date_lesson)' +
                  'values (?,?,?,?,?,?)', (id_lesson, id_teacher, id_time, 1, id_group, par.date_lesson))
        self.CONN.commit()
        c.close()
        self.conn_open_close(0)

    def get_all_info_about_user(self, tg_id):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        result = c.execute('SELECT s.tg_id, s.tg_username, s.is_admin, g.name FROM USERS s, GROUPS g WHERE s.id_group=g.id and s.tg_id = ?', (tg_id,)).fetchone()
        c.close()
        self.conn_open_close(0)
        return result

    def get_all_groups(self):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        result = c.execute('SELECT name FROM GROUPS').fetchall()
        c.close()
        self.conn_open_close(0)
        return result

    def set_group_and_tg_id_user(self, group, username, tg_id):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        id_group = c.execute('SELECT id FROM GROUPS WHERE name = ?', (group,)).fetchone()[0]
        is_tg_id = c.execute('SELECT tg_id FROM USERS WHERE tg_id = ?', (tg_id,)).fetchone()
        if is_tg_id is None:
            c.execute('UPDATE USERS set id_group = ?, tg_id = ? where tg_username = ?', (id_group, tg_id, username))
        else:
            c.execute('UPDATE USERS set id_group = ?, tg_username = ? where tg_id = ?', (id_group, username, tg_id))
        self.CONN.commit()
        c.close()
        self.conn_open_close(0)

    def insert_users(self, username, is_admin=False):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        c.execute('INSERT INTO USERS (tg_username, is_admin) VALUES (?, ?)', (username, is_admin))
        self.CONN.commit()
        c.close()
        self.conn_open_close(0)

    def get_next_date(self, flag, date):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        result = ''

        if flag == '1':
            result = c.execute('SELECT DISTINCT date_lesson FROM TIMETABLES where date(date_lesson) > date(?) order by date_lesson',
                               (date,)).fetchone()
        elif flag == '0':
            result = c.execute('SELECT DISTINCT date_lesson FROM TIMETABLES where date(date_lesson) < date(?) order by date_lesson desc',
                               (date,)).fetchone()
        c.close()
        self.conn_open_close(0)

        if result is None:
            return None

        return result[0]

    def get_timetable_dates(self):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        result = c.execute('SELECT DISTINCT date_lesson FROM TIMETABLES').fetchall()
        c.close()
        self.conn_open_close(0)
        return result

    def get_timetable(self, tg_id, date=None):
        self.conn_open_close(1)
        c = self.CONN.cursor()

        id_group = c.execute('SELECT id_group FROM USERS where tg_id = ?', (tg_id,)).fetchone()[0]

        if date is None:
            date = Utils.get_date_now()

            i = 1
            while True:
                if i == 30:
                    return None
                res = c.execute('SELECT id FROM TIMETABLES where date_lesson = ? and id_group = ?', (date, id_group)).fetchone()
                if res is None:
                    date = Utils.get_date_now(i)
                    i += 1
                else:
                    break

        result = c.execute(
            'SELECT s.date_lesson, l.name, t.name, ts.time, g.name FROM TIMETABLES s, TIMES ts, TEACHERS t, LESSONS l, GROUPS g WHERE s.id_group = g.id and s.date_lesson = ? and s.id_group = ? and ts.id = s.id_time and t.id = s.id_teacher and l.id = s.id_lesson ORDER BY s.id',
            (date, id_group)).fetchall()
        c.close()
        self.conn_open_close(0)

        data_pars = []
        for par in result:
            data_pars.append(Pars(par[0], par[1], par[4], par[3], par[2]))
        return data_pars

    def get_timetables(self, date, group):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        id_group = c.execute('SELECT id FROM GROUPS where name = ?', (group,)).fetchone()[0]
        result = c.execute('SELECT s.date_lesson, l.name, t.name, ts.time FROM TIMETABLES s, TIMES ts, TEACHERS t, LESSONS l WHERE s.date_lesson = ? and s.id_group = ? and ts.id = s.id_time and t.id = s.id_teacher and l.id = s.id_lesson', (date, id_group)).fetchall()
        c.close()
        self.conn_open_close(0)

        data_pars = []
        for par in result:
            data_pars.append(Pars(par[0], par[1], group, par[3], par[2]))
        return data_pars

    def is_admin(self, tg_id):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        result = c.execute('SELECT is_admin FROM USERS WHERE tg_id = ?', (tg_id,)).fetchone()[0]
        c.close()
        self.conn_open_close(0)
        return result

    def is_user(self, tg_id=None, username=None):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        result = None
        if tg_id is not None:
            result = c.execute('SELECT TG_ID FROM USERS WHERE TG_ID = ?', (tg_id,)).fetchone()
        elif username is not None:
            result = c.execute('SELECT TG_ID FROM USERS WHERE tg_username = ?', (username,)).fetchone()
        c.close()
        self.conn_open_close(0)
        if result is not None:
            return True
        return False

    def insert_init(self):
        self.conn_open_close(1)
        c = self.CONN.cursor()
        try:
            c.executescript("""
                INSERT OR REPLACE INTO TIMES (id,time) VALUES (1,"09:10-10:30");
                INSERT OR REPLACE INTO TIMES (id,time) VALUES (2,"10:40-12:00");
                INSERT OR REPLACE INTO TIMES (id,time) VALUES (3,"12:40-14:00");
                INSERT OR REPLACE INTO TIMES (id,time) VALUES (4,"14:10-15:30");
                INSERT OR REPLACE INTO TIMES (id,time) VALUES (5,"15:40-17:00");
                INSERT OR REPLACE INTO TIMES (id,time) VALUES (6,"17:10-18:30");
                INSERT OR REPLACE INTO TIMES (id,time) VALUES (7,"18:40-20:00");
                INSERT OR REPLACE INTO TIMES (id,time) VALUES (8,"20:10-21:30");
                INSERT OR REPLACE INTO GROUPS (id,name) VALUES (1,"ПИ-20СВ-1(16)");
                INSERT OR REPLACE INTO GROUPS (id,name) VALUES (2,"ПИ-20СВ-2 (15)");
            """)
            self.CONN.commit()
        except Error as e:
            pass

        c.close()
        self.conn_open_close(0)

    def conn_open_close(self, stat):
        if stat == 1:
            self.CONN = sqlite3.connect(self.DBFILE)
        else:
            self.CONN.close()

    def create_tables(self):
        try:
            self.conn_open_close(1)
            c = self.CONN.cursor()
            c.execute(f'{self.CREATE_TABLE} TIMES (id {self.INT} {self.PK} {self.AUTOINCREMENT}, time {self.TEXT})')
            c.execute(f'{self.CREATE_TABLE} CLASSROOMS (id {self.INT} {self.PK} {self.AUTOINCREMENT}, name {self.TEXT})')
            c.execute(f'{self.CREATE_TABLE} TEACHERS (id {self.INT} {self.PK} {self.AUTOINCREMENT}, name {self.TEXT})')
            c.execute(f'{self.CREATE_TABLE} LESSONS (id {self.INT} {self.PK} {self.AUTOINCREMENT}, name {self.TEXT})')
            c.execute(f'{self.CREATE_TABLE} GROUPS (id {self.INT} {self.PK} {self.AUTOINCREMENT}, name {self.TEXT})')
            c.execute(f'{self.CREATE_TABLE} TIMETABLES (id {self.INT} {self.PK} {self.AUTOINCREMENT}, '
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
            c.execute(f'{self.CREATE_TABLE} USERS (tg_id {self.INT}, tg_username {self.TEXT} {self.PK}, '
                      f'is_admin {self.BOOL}, id_group {self.INT}, message_id {self.TEXT}'
                      f'{self.FK} (id_group) {self.REFERENCES} GROUPS (id))')
            c.close()
            self.conn_open_close(0)
        except Error as e:
            pass

    def __init__(self):
        self.create_tables()
        self.insert_init()
