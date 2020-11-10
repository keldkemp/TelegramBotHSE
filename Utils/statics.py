"""
Класс для работы с статистикой.
"""
from Utils.logging import Logging
from Utils.utils import Utils


class Statics:

    def insert_request(self):
        try:
            date = Utils.get_date_now()
            self.__db.insert_stat(date)
        except Exception as e:
            self.__log.input_log(Utils.get_date_now_sec() + ' ' + str(e))

    def __init__(self, db):
        self.__db = db
        self.__log = Logging()
