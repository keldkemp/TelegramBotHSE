"""
Вспомогательный класс - Часто встречаемые функции.
"""
import datetime
import os
from win32com.client import Dispatch


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
    def convert_xls_to_xlsx(file_name, new_file_name):
        xlApp = Dispatch('Excel.Application')
        xlApp.Visible = 0
        xlApp.DisplayAlerts = False
        xlApp.Workbooks.Open(os.path.abspath(file_name))  # An xls file.
        xlApp.ActiveWorkbook.SaveAs(os.getcwd() + '\\' + new_file_name, FileFormat=51,
                                    ConflictResolution=2)  # 51=xlsx, 2=overwrite
        xlApp.ActiveWorkbook.Close()
        xlApp.Quit()

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
