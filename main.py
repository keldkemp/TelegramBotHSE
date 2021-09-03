"""
Базовый файл для запуска всего проекта.
TODO: Избавиться от дополнительных методов в этом файле
"""
import datetime
import subprocess
import sys
import threading
from DB.DataBasePG import DataBasePg
from Emails.emails import Email
from HseUtils.HseTelegram import HseTelegram
from Utils.logging import Logging
from Settings import SettingsTelegram, SettingsEmail
from Utils.statics import Statics
from Telegram import TelegramApi
from Utils.utils import Utils


def groups_msg(result):
    call_back_id = None
    try:
        last_text = result[0]['message']['text']
        last_chat_id = result[0]['message']['chat']['id']
        message_id = result[0]['message']['message_id']
    except:
        try:
            last_text = result[0]['callback_query']['data']
        except:
            return 0
        last_chat_id = result[0]['callback_query']['message']['chat']['id']
        call_back_id = result[0]['callback_query']['id']
        message_id = result[0]['callback_query']['message']['message_id']

    if db.is_user(tg_id=int(last_chat_id)):
        if last_text.find('/timetables') != -1:
            hseTelegram.timetables_now(last_chat_id=last_chat_id, message_id=message_id)
        elif last_text.find('/corps') != -1:
            hseTelegram.get_all_corps(last_chat_id=last_chat_id, type='group')
        elif last_text.find('par_dates_list') != -1:
            telegram.answer_callback(call_back_id)
            hseTelegram.timetables_date(last_chat_id=last_chat_id, last_text=last_text)
    else:
        telegram.send_msg(last_chat_id, f'Возникли проблемы, обратитесь к @keldkemp\nErrorCode: 2\nID: {last_chat_id}')


def private_msg(result):
    call_back_id = None
    try:
        last_text = result[0]['message']['text']
        last_chat_id = result[0]['message']['chat']['id']
        message_id = result[0]['message']['message_id']
        try:
            username = result[0]['message']['chat']['username']
        except:
            if db.is_user(tg_id=int(last_chat_id)):
                username = ''
            else:
                telegram.send_msg(last_chat_id, 'Возникли проблемы, обратитесь к @keldkemp\nErrorCode: 1')
                return 0
    except:
        try:
            last_text = result[0]['callback_query']['data']
        except:
            return 0
        last_chat_id = result[0]['callback_query']['message']['chat']['id']
        call_back_id = result[0]['callback_query']['id']
        message_id = result[0]['callback_query']['message']['message_id']
        try:
            username = result[0]['callback_query']['message']['chat']['username']
        except:
            if db.is_user(tg_id=int(last_chat_id)):
                username = ''
            else:
                telegram.send_msg(last_chat_id, 'Возникли проблемы, обратитесь к @keldkemp\nErrorCode: 1')
                return 0

    # Запускаем потоки
    threading.Thread(target=razbor, args=(last_chat_id, call_back_id, username, last_text, message_id)).start()


def razbor(last_chat_id, call_back_id, username, last_text, message_id):
    if db.is_user(tg_id=int(last_chat_id)) and db.is_activate(tg_id=last_chat_id):
        if last_text.find('Группа//') != -1:
            telegram.answer_callback(call_back_id)
            group = last_text.replace('Группа// ', '')
            hseTelegram.update_group(last_chat_id=last_chat_id, group=group, username=username, message_id=message_id)
        elif last_text.find('ChangeGroup_Курс//') != -1:
            telegram.answer_callback(call_back_id)
            hseTelegram.change_group(last_chat_id=last_chat_id, username=username, last_text=last_text, message_id=message_id)
        elif not db.is_group(tg_id=last_chat_id) or last_text == 'ChangeGroups//':
            telegram.answer_callback(call_back_id)
            hseTelegram.change_group_main(last_chat_id=last_chat_id, username=username)
        elif last_text == 'Расписание' or last_text.find('/timetables') != -1:
            hseTelegram.timetables_now(last_chat_id=last_chat_id, message_id=message_id)
        elif last_text.find('par_dates_list') != -1:
            telegram.answer_callback(call_back_id)
            hseTelegram.timetables_date(last_chat_id=last_chat_id, last_text=last_text)
        elif last_text == 'Настройки':
            hseTelegram.settings(last_chat_id=last_chat_id)
        elif last_text == 'Корпуса' or last_text.find('/corps') != -1:
            hseTelegram.get_all_corps(last_chat_id=last_chat_id)
        elif last_text.lower().find('add') != -1 and db.is_admin(last_chat_id) == 1:
            hseTelegram.add_users(last_chat_id=last_chat_id, last_text=last_text)
        elif last_text.lower().find('sendallmsg') != -1 and db.is_admin(last_chat_id) == 1:
            indx = last_text.find(' ')
            msg = last_text[indx + 1:]
            hseTelegram.send_all_users_msg(msg)
        elif last_text.lower().find('statics') != -1 and db.is_admin(last_chat_id) == 1:
            hseTelegram.get_stat(last_chat_id=last_chat_id)
        elif last_text.lower().find('updatetimetable') != -1 and db.is_admin(last_chat_id) == 1:
            hseTelegram.update_timetable(last_chat_id=last_chat_id)
        elif last_text.lower().find('list') != -1 and db.is_admin(last_chat_id) == 1:
            hseTelegram.list_command_admin(last_chat_id)
        else:
            telegram.send_msg(last_chat_id, 'main', telegram.main_keyboard)
    elif last_text == 'NotSendEmail//':
        telegram.answer_callback(call_back_id)
        hseTelegram.resend_email(last_chat_id=last_chat_id)
    elif db.is_user(tg_id=int(last_chat_id)):
        hseTelegram.input_code(last_chat_id=last_chat_id, last_text=last_text)
    elif last_text.find('@') != -1:
        hseTelegram.auth_in_tg(last_chat_id=last_chat_id, last_text=last_text, username=username)
    else:
        telegram.send_msg(last_chat_id, f'Чтобы авторизоваться в боте, необходимо указать Email в домене HSE')


if __name__ == '__main__':
    threading.stack_size(128 * 1024)
    db = DataBasePg()
    settings = SettingsEmail().get_settings_email()
    email = Email(login=settings['login'], password=settings['password'], host=settings['host'], port=settings['port'])
    log = Logging()
    statics = Statics(db)
    settings = SettingsTelegram().get_settings_tg()
    telegram = TelegramApi(settings['token'])
    hseTelegram = HseTelegram(db, telegram, email)
    offset = None
    call_back_id = None
    admin_id = 453256909
    date = datetime.datetime.now()
    subprocess.Popen([sys.executable, 'UpdateTimeTable.py'])

    while True:
        if date < datetime.datetime.now() - datetime.timedelta(hours=1):
            subprocess.Popen([sys.executable, 'UpdateTimeTable.py'])
            print('SUCCSES')
            date = datetime.datetime.now()
        result = telegram.get_updates(offset=offset)
        if not result:
            continue
        last_update_id = result[0]['update_id']
        offset = last_update_id + 1

        # Статистика запросов
        threading.Thread(target=statics.insert_request).start()

        try:
            try:
                if result[0]['message']['chat']['type'] == 'supergroup' or result[0]['message']['chat']['type'] == 'group':
                    threading.Thread(target=groups_msg, args=(result,)).start()
                    continue
            except:
                if result[0]['callback_query']['message']['chat']['type'] == 'supergroup' or \
                        result[0]['callback_query']['message']['chat']['type'] == 'group':
                    threading.Thread(target=groups_msg, args=(result,)).start()
                    continue

            threading.Thread(target=private_msg, args=(result,)).start()
        except Exception as e:
            log.input_log(Utils.get_date_now_sec() + ' ' + str(e))
            continue
