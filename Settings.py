"""
Классы для работы с настройками проекта.
Настройки берутся из файла
"""
import json
import os
import urllib.parse as urlparse
from abc import ABC
from Utils.utils import Utils


# Абстрактный класс по работе с настройками
class Settings(ABC):
    __FILE_NAME = 'settings.json'

    def __read_file(self) -> json:
        f = open('settings.json')
        str = f.read()
        f.close()
        return json.loads(str)

    def __read_env(self) -> json:
        dc = {}
        dc['telegram_token'] = os.environ['telegram_token']
        if os.environ.get('db_name') is not None:
            dc['db_name'] = os.environ['db_name']
            dc['db_user'] = os.environ['db_user']
            dc['db_password'] = os.environ['db_password']
            dc['host'] = os.environ['host']
        else:
            url_db = urlparse.urlparse(os.environ['DATABASE_URL'])
            dc['db_name'] = url_db.path[1:]
            dc['db_user'] =url_db.username
            dc['db_password'] = url_db.password
            dc['host'] = url_db.hostname
        dc['login_email'] = os.environ['login_email']
        dc['password_email'] = os.environ['password_email']
        dc['host_email'] = os.environ['host_email']
        dc['port_email'] = os.environ['port_email']
        return dc

    def __init__(self):
        json_settings = self.__read_file() if os.path.exists(self.__FILE_NAME) else self.__read_env()
        self._token = json_settings['telegram_token']
        self._db_name = json_settings['db_name']
        self._db_user = json_settings['db_user']
        self._db_password = json_settings['db_password']
        self._host = json_settings['host']
        if os.environ.get('is_email') is not None:
            is_email = Utils.get_bool(os.environ['is_email'])
            if is_email:
                self._login_email = json_settings['login_email']
                self._password_email = json_settings['password_email']
                self._host_email = json_settings['host_email']
                self._port_email = json_settings['port_email']


# класс для получения настроек для Почты. Наследуется от базового класса
class SettingsEmail(Settings):
    def get_settings_email(self) -> dict:
        list = {'login': self._login_email, 'password': self._password_email, 'host': self._host_email,
                'port': self._port_email}
        return list


# класс для получения настроек для ТГ. Наследуется от базового класса
class SettingsTelegram(Settings):
    def get_settings_tg(self) -> dict:
        list = {'token': self._token}
        return list


# класс для получения настроек для БД. Наследуется от базового класса
class SettingsDb(Settings):
    def get_settings_db(self) -> dict:
        list = {'db_name': self._db_name, 'db_user': self._db_user, 'db_password': self._db_password,
                'host': self._host}
        return list
