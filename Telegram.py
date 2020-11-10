"""
Класс для работы с Telegram.
Пока не совсем отдельно существующий класс, клавиатура захардкорена, как нибудь сделаю в кастом.
Для инициализации необходимо передать Токен.
"""
import requests
import json


class TelegramApi:
    __TOKEN = None
    __BASE_URL = 'https://api.telegram.org/bot'
    session = requests.session()

    # TODO: Убрать клавиатуру в кастом
    main_keyboard = json.dumps({'keyboard': [[{'text': 'Расписание'}],
                                             [{'text': 'Настройки'}],
                                             [{'text': 'Корпуса'}]],
                                'resize_keyboard': True, 'one_time_keyboard': True})
    settings_keyboard = json.dumps(
        {'inline_keyboard': [[{'text': 'Сменить группу', 'callback_data': 'ChangeGroups//'}]]})

    def delete_msg(self, chat_id, message_id):
        data = {'chat_id': chat_id, 'message_id': message_id}
        r = self.session.post(self.__BASE_URL + 'deleteMessage', data=data)
        return json.loads(r.text)

    def edit_msg(self, chat_id, message_id, msg, reply_markup=None):
        data = {'chat_id': chat_id, 'message_id': message_id, 'text': msg, 'parse_mode': 'HTML',
                'reply_markup': reply_markup}
        r = self.session.post(self.__BASE_URL + 'editMessageText', data=data)
        return json.loads(r.text)

    def send_msg(self, chat_id, msg, reply_markup=None):
        data = {'chat_id': chat_id, 'text': msg, 'parse_mode': 'HTML', 'reply_markup': reply_markup}
        r = self.session.post(self.__BASE_URL + 'sendMessage', data=data)
        return json.loads(r.text)

    def get_updates(self, timeout=30, offset=None):
        try:
            data = {'timeout': timeout, 'offset': offset}
            r = self.session.post(self.__BASE_URL + 'getUpdates', data=data)
            return json.loads(r.text)['result']
        except ConnectionError:
            print('ConnectionError GetUpdates')
            pass

    def answer_callback(self, id):
        data = {'callback_query_id': id}
        r = self.session.post(self.__BASE_URL + 'answerCallbackQuery', data=data)
        return json.loads(r.text)

    def __init__(self, token):
        self.__TOKEN = token
        self.__BASE_URL = self.__BASE_URL + self.__TOKEN + '/'
