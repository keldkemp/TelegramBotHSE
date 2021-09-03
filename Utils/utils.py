"""
Вспомогательный класс - Часто встречаемые функции.
"""
import datetime
import os
import random
from os import walk


class Utils:
    DAYS = {
        0: 'Понедельнки',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье'
    }

    @staticmethod
    def get_bool(bool_str: str) -> bool:
        if bool_str.upper() == 'TRUE':
            return True
        else:
            return False

    @staticmethod
    def get_date_now_sec() -> str:
        return str(datetime.datetime.now())

    @staticmethod
    def get_date_now(days=None) -> str:
        date_d = datetime.datetime.now()

        if days is not None:
            date_d += datetime.timedelta(days=days)

        if len(str(date_d.month)) == 1:
            month = '0' + str(date_d.month)
        else:
            month = str(date_d.month)

        if len(str(date_d.day)) == 1:
            day = '0' + str(date_d.day)
        else:
            day = str(date_d.day)

        date = str(date_d.year) + '-' + month + '-' + day

        return date

    @staticmethod
    def date_op_days(date: str, days: int, op: str) -> str:
        date_d = datetime.datetime.strptime(date, '%Y-%m-%d')
        new_date_str = ''
        if op == 'minus':
            new_date = date_d - datetime.timedelta(days=days)
            new_date_str = datetime.datetime.strftime(new_date, '%Y-%m-%d')
        elif op == 'plus':
            new_date = date_d + datetime.timedelta(days=days)
            new_date_str = datetime.datetime.strftime(new_date, '%Y-%m-%d')
        return new_date_str

    @staticmethod
    def comparison_date(date_str: str) -> bool:
        date_now = datetime.date.today()
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

        if date_now > date:
            return False
        return True

    @staticmethod
    def get_day_from_date(date_str: str) -> str:
        date_d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        week_day = date_d.weekday()
        week_day = Utils.DAYS.get(week_day)
        return week_day

    @staticmethod
    def get_year_from_date(date_str: str) -> int:
        date_d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        year = date_d.year
        return year

    @staticmethod
    def get_date_from_course(course: str) -> str:
        date_d = datetime.datetime.now()
        date_d = date_d.replace(year=date_d.year - int(course) + 1)

        if len(str(date_d.month)) == 1:
            month = '0' + str(date_d.month)
        else:
            month = str(date_d.month)

        if len(str(date_d.day)) == 1:
            day = '0' + str(date_d.day)
        else:
            day = str(date_d.day)

        date = str(date_d.year) + '-' + month + '-' + day

        return date

    @staticmethod
    def read_migrations() -> list:
        cwd = os.getcwd()
        path = cwd + '/Migrations/'
        migrations_list = []
        for _, _, filenames in walk(path):
            for file in filenames:
                if file == 'create_migrations.py':
                    continue
                else:
                    f = open(path + file, 'r')
                    migrations_list.append(f.readlines()[0])
                    f.close()
        return migrations_list

    @staticmethod
    def generate_unic_code() -> int:
        random.seed()
        number = round(random.random() * 1000000)
        if len(str(number)) < 6:
            number *= 10
        return number
