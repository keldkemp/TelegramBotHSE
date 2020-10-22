import requests
import json


class TelegramApi:
    __TOKEN = None
    BASE_URL = 'https://api.telegram.org/bot'
    session = requests.session()

    main_keyboard = json.dumps({'keyboard': [[{'text': 'Расписание'}],
                                             [{'text': 'Настройки'}],
                                             [{'text': 'Корпуса'}]],
                                'resize_keyboard': True, 'one_time_keyboard': True})
    settings_keyboard = json.dumps(
        {'inline_keyboard': [[{'text': 'Сменить группу', 'callback_data': 'ChangeGroups//'}]]})

    def delete_msg(self, chat_id, message_id):
        data = {'chat_id': chat_id, 'message_id': message_id}
        r = self.session.post(self.BASE_URL + 'deleteMessage', data=data)
        return json.loads(r.text)

    def edit_msg(self, chat_id, message_id, msg, reply_markup=None):
        data = {'chat_id': chat_id, 'message_id': message_id, 'text': msg, 'parse_mode': 'HTML',
                'reply_markup': reply_markup}
        r = self.session.post(self.BASE_URL + 'editMessageText', data=data)
        return json.loads(r.text)

    def send_msg(self, chat_id, msg, reply_markup=None):
        data = {'chat_id': chat_id, 'text': msg, 'parse_mode': 'HTML', 'reply_markup': reply_markup}
        r = self.session.post(self.BASE_URL + 'sendMessage', data=data)
        return json.loads(r.text)

    def get_updates(self, timeout=30, offset=None):
        data = {'timeout': timeout, 'offset': offset}
        r = self.session.post(self.BASE_URL + 'getUpdates', data=data)
        return json.loads(r.text)['result']

    def answer_callback(self, id):
        data = {'callback_query_id': id}
        r = self.session.post(self.BASE_URL + 'answerCallbackQuery', data=data)
        return json.loads(r.text)

    def __init__(self, token):
        self.__TOKEN = token
        self.BASE_URL = self.BASE_URL + self.__TOKEN + '/'
