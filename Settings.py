import json
from abc import ABC


class Settings(ABC):

    def __read_file(self) -> json:
        f = open('settings.json')
        str = f.read()
        f.close()
        return json.loads(str)

    def __init__(self):
        json_settings = self.__read_file()
        self._token = json_settings['telegram_token']
        self._db_name = json_settings['db_name']
        self._db_user = json_settings['db_user']
        self._db_password = json_settings['db_password']
        self._host = json_settings['host']


class SettingsTelegram(Settings):
    def get_settings_tg(self) -> dict:
        list = {'token': self._token}
        return list


class SettingsDb(Settings):
    def get_settings_db(self) -> dict:
        list = {'db_name': self._db_name, 'db_user': self._db_user, 'db_password': self._db_password, 'host': self._host}
        return list
