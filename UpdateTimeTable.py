from DataBasePG import DataBasePg
from Settings import SettingsTelegram
from Telegram import TelegramApi
from get_files import HSE

hse = HSE()
db = DataBasePg()
setting = SettingsTelegram().get_settings_tg()
tg = TelegramApi(setting['token'])
admin_id = 453256909

try:
    html = hse.get_html('https://perm.hse.ru/forstudents/timetable/')
    urls = hse.get_urls(html)
    data_pars = hse.download_files(urls)

    date = []
    for pars in data_pars:
        for par in pars:
            date.append(par.date_lesson)

    date = list(set(date))
    db.delete_timetables_date(date)

    for pars in data_pars:
        for par in pars:
            db.insert_timetables(par)
    #tg.send_msg(admin_id, 'TimeTables is update success')
except Exception as error:
    tg.send_msg(admin_id, 'ERROR:\n' + str({error}))
