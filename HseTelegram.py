import subprocess
import sys
from DataBasePG import DataBasePg
from Telegram import TelegramApi
from Utils import Utils
from Logging import Logging


class HseTelegram:
    __MSG_ERROR = 'Что-то пошло не так. Пожалуйста, скажите об этом администратору: @KeldKemp\n\nErrorCode: '
    __ERROR_COD_UPDATE_GROUP = '11'
    __ERROR_MSG_UPDATE_GROUP = '\nНе удается обновить группу!'
    __ERROR_COD_SETTINGS = '12'
    __ERROR_MSG_SETTINGS = '\nНе удается открыть настройки!'
    __ERROR_COD_CHANGE_GROUP = '13'
    __ERROR_MSG_CHANGE_GROUP = '\nНе удается сменить группу!'
    __ERROR_COD_TIMETABLES = '14'
    __ERROR_MSG_TIMETABLES = '\nНе удается найти расписание!'
    __ERROR_COD_TIMETABLES_DATE = '15'
    __ERROR_MSG_TIMETABLES_DATE = '\nНе удается найти расписание на следующую дату!'
    __ERROR_COD_CORPS = '16'
    __ERROR_MSG_CORPS = '\nНе удается нати корпуса!'
    __log = Logging()
    __admin_id = 453256909
    __GROUP = 'group'
    __PRIVATE = 'private'

    def set_scheduler(self, last_chat_id):
        # TODO: Кастомные уведомления
        pass

    def update_timetable(self, last_chat_id):
        try:
            subprocess.Popen([sys.executable, 'UpdateTimeTable.py'])
            self.__telegram.send_msg(last_chat_id, 'Расписание обновлено!')
        except Exception as e:
            self.__log.input_log(Utils.get_date_now_sec() + ' ' + str(e))

    def get_stat(self, last_chat_id):
        try:
            date = Utils.get_date_now()
            stat = self.__db.get_stat(date_from=date, date_to=date)
            req = stat[0][0]
            msg = f'Статистика\n\nОбращений: {req}\nДата: {date}'
            self.__telegram.send_msg(chat_id=last_chat_id, msg=msg)
        except Exception as e:
            self.__telegram.send_msg(last_chat_id, 'Не удается получить статистику!')
            self.__log.input_log(Utils.get_date_now_sec() + ' ' + str(e))

    def get_all_corps(self, last_chat_id, type=None):
        try:
            corps = self.__db.get_all_corp()
            msg = ''
            for corp in corps:
                msg += corp[0] + '\n'
            if type is None:
                self.__telegram.send_msg(last_chat_id, msg, self.__telegram.main_keyboard)
            elif type == self.__GROUP:
                self.__telegram.send_msg(last_chat_id, msg)
        except Exception as e:
            self.__telegram.send_msg(last_chat_id, self.__MSG_ERROR + self.__ERROR_COD_CORPS + self.__ERROR_MSG_CORPS)
            self.__log.input_log(Utils.get_date_now_sec() + ' ' + str(e))

    def send_all_users_msg(self, msg):
        try:
            users = self.__db.get_all_user()
            for user in users:
                self.__telegram.send_msg(user[0], msg)
        except Exception as e:
            self.__telegram.send_msg(self.__admin_id, 'Ошибка массовой отправки')
            self.__log.input_log(Utils.get_date_now_sec() + ' ' + str(e))

    def timetables_date(self, last_chat_id, last_text):
        try:
            txt = last_text.split()
            flag = txt[1]
            date_r = txt[3]
            message__id = int(txt[2])

            date = self.__db.get_next_date(flag, date_r, last_chat_id)
            if date is None:
                if flag == '1':
                    msg = 'На более позднии даты расписания нет'
                    date = Utils.date_op_days(date_r, 1, 'plus')
                    key = '{"inline_keyboard": [[{"text": "⬅", "callback_data": "par_dates_list 0 %i %s"}]]}' % (
                        message__id, date)
                    self.__telegram.edit_msg(last_chat_id, message__id, msg, key)
                else:
                    msg = 'На более рании даты расписания нет'
                    date = Utils.date_op_days(date_r, 1, 'minus')
                    key = '{"inline_keyboard": [[{"text": "➡", "callback_data": "par_dates_list 1 %i %s"}]]}' % (
                        message__id, date)
                    self.__telegram.edit_msg(last_chat_id, message__id, msg, key)
                return 0

            timetable = self.__db.get_timetable(last_chat_id, date)
            msg = ''

            if timetable is None:
                msg = 'Пар нету ближайшие 30 дней'
                self.__telegram.send_msg(last_chat_id, msg)
                return 0
            else:
                i = 1
                for par in timetable:
                    if i == 1:
                        msg = f'Расписание на <b>{par.date_lesson}</b>\n\n'
                    lesson = par.lesson.replace('\n', ' ')
                    msg += f'{i}) <b>{par.time}</b> - {lesson} - {par.teacher}\n'
                    i += 1
            key = '{"inline_keyboard": [[{"text": "⬅", "callback_data": "par_dates_list 0 %i %s"}, {"text": "➡", ' \
                  '"callback_data": "par_dates_list 1 %i %s"}]]}' % (
                      message__id, par.date_lesson, message__id, par.date_lesson)
            self.__telegram.edit_msg(last_chat_id, message__id, msg, key)
        except Exception as e:
            self.__telegram.send_msg(last_chat_id, self.__MSG_ERROR + self.__ERROR_COD_TIMETABLES_DATE +
                                     self.__ERROR_MSG_TIMETABLES_DATE)
            self.__log.input_log(Utils.get_date_now_sec() + ' ' + str(e))

    def timetables_now(self, last_chat_id, message_id):
        try:
            timetable = self.__db.get_timetable(last_chat_id)
            msg = ''

            if timetable is None:
                msg = 'Пар нету ближайшие 30 дней'
                self.__telegram.send_msg(last_chat_id, msg)
                return 0
            else:
                i = 1
                for par in timetable:
                    if i == 1:
                        msg = f'Расписание на <b>{par.date_lesson}</b>\n\n'
                    lesson = par.lesson.replace('\n', ' ')
                    msg += f'{i}) <b>{par.time}</b> - {lesson} - {par.teacher}\n'
                    i += 1

            key = '{"inline_keyboard": [[{"text": "⬅", "callback_data": "par_dates_list 0 %i %s"}, {"text": "➡", ' \
                  '"callback_data": "par_dates_list 1 %i %s"}]]}' % (
                      message_id + 1, par.date_lesson, message_id + 1, par.date_lesson)
            self.__telegram.send_msg(last_chat_id, msg, key)
        except Exception as e:
            self.__telegram.send_msg(last_chat_id, self.__MSG_ERROR + self.__ERROR_COD_TIMETABLES +
                                     self.__ERROR_MSG_TIMETABLES)
            self.__log.input_log(Utils.get_date_now_sec() + ' ' + str(e))

    def change_group(self, last_chat_id, username):
        try:
            groups = ''
            ar_txt = '['
            i = 1
            for group in self.__db.get_all_groups():
                groups = groups + str(i) + ') ' + group[0] + '\n'
                if i == 1:
                    ar_txt = ar_txt + '[{"text": %d, "callback_data": "Группа// %s"}' % (i, group[0])
                else:
                    ar_txt = ar_txt + ',{"text": %d, "callback_data": "Группа// %s"}' % (i, group[0])
                i += 1
            ar_txt = ar_txt + ']]'
            key = '{"inline_keyboard":' + ar_txt + '}'

            self.__telegram.send_msg(last_chat_id, username + ', выберите свою группу:\n' + groups, key)
        except Exception as e:
            self.__telegram.send_msg(last_chat_id, self.__MSG_ERROR + self.__ERROR_COD_CHANGE_GROUP +
                                     self.__ERROR_MSG_CHANGE_GROUP)
            self.__log.input_log(Utils.get_date_now_sec() + ' ' + str(e))

    def update_group(self, last_chat_id, group, username, message_id):
        try:
            self.__db.set_group_and_tg_id_user(group, username, last_chat_id)
            self.__telegram.delete_msg(last_chat_id, message_id)
            self.__telegram.send_msg(last_chat_id, f'Вы выбрали группу {group}', self.__telegram.main_keyboard)
        except Exception as e:
            self.__telegram.send_msg(last_chat_id, self.__MSG_ERROR + self.__ERROR_COD_UPDATE_GROUP +
                                     self.__ERROR_MSG_UPDATE_GROUP)
            self.__log.input_log(Utils.get_date_now_sec() + ' ' + str(e))

    def add_users(self, last_chat_id, last_text):
        try:
            arr = last_text.split()
            username = arr[1]
            is_admin = arr[2]
            if username[0] == '-' and username[1].isdigit():
                id_group = arr[3]
                self.__db.insert_users(username=username, is_only_tgid=True, id_group=id_group)
            elif username.isdigit():
                id_group = arr[3]
                self.__db.insert_users(username=username, is_only_tgid=False, id_group=id_group)
            else:
                if is_admin == 1:
                    self.__db.insert_users(username, True)
                else:
                    self.__db.insert_users(username)
            self.__telegram.send_msg(last_chat_id, 'Пользователь ' + username + ' успешно добавлен!')
        except Exception as e:
            self.__telegram.send_msg(last_chat_id, f'Что-то пошло не так\n{e}')
            self.__log.input_log(Utils.get_date_now_sec() + ' ' + str(e))

    def settings(self, last_chat_id):
        try:
            info_user = self.__db.get_all_info_about_user(last_chat_id)
            tg_id = info_user[0]
            username = info_user[1]
            is_admin = (False, True)[info_user[2] == 1]
            group = info_user[3]
            if is_admin:
                msg = f'ИД: {tg_id}\nusername: {username}\nГруппа: {group}\nAdmin: {is_admin}'
            else:
                msg = f'ИД: {tg_id}\nusername: {username}\nГруппа: {group}'
            self.__telegram.send_msg(last_chat_id, msg, self.__telegram.settings_keyboard)
        except Exception as e:
            self.__telegram.send_msg(last_chat_id, self.__MSG_ERROR + self.__ERROR_COD_SETTINGS +
                                     self.__ERROR_MSG_SETTINGS)
            self.__log.input_log(Utils.get_date_now_sec() + ' ' + str(e))

    def __init__(self, db: DataBasePg, telegram: TelegramApi):
        self.__db = db
        self.__telegram = telegram
