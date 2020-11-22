"""
Данный файл запускается по крону. Он необходим для обнволения расписания.
Здесь мы подключаем модули:
    Базу Данных(projectFolder/DB/*),
    Настройки(projectFolder/*),
    Hse(projectFolder/HseUtils)
"""
from DB.DataBasePG import DataBasePg
from Settings import SettingsTelegram
from Telegram import TelegramApi
from HseUtils.HseFiles import HSE

# Инициализируем классы
hse = HSE()
db = DataBasePg()
setting = SettingsTelegram().get_settings_tg()
tg = TelegramApi(setting['token'])
admin_id = 453256909

try:
    # скачиваем excel
    html = hse.get_html('https://perm.hse.ru/forstudents/timetable/')
    urls = hse.get_urls(html)
    data_pars = hse.download_files(urls)

    # достаем даты занятий
    date = []
    groups = []
    for group_pars in data_pars:
        for pars in group_pars:
            for par in pars:
                groups.append(par.group)
                date.append(par.date_lesson)
    # удаляем из БД данные по текущим датам
    date = list(set(date))
    groups = list(set(groups))
    db.delete_timetables_date(date, groups)

    # Заполняем новыми данными
    for group_pars in data_pars:
        for pars in group_pars:
            for par in pars:
                db.insert_timetables(par)
    # tg.send_msg(admin_id, 'TimeTables is update success')
except Exception as error:
    tg.send_msg(admin_id, 'ERROR:\n' + str({error}))
