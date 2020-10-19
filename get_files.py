from datetime import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import os
from models.Models import Pars


class HSE:
    BASE_URL = 'https://perm.hse.ru'
    FILE_NAME = 'file_test.xls'
    RU_MONTH_VALUES = {
        'января': '01',
        'февраля': '02',
        'марта': '03',
        'апреля': '04',
        'мая': '05',
        'июня': '06',
        'июля': '07',
        'августа': '08',
        'сентября': '09',
        'октября': 10,
        'ноября': 11,
        'декабря': 12,
    }

    def __parse_xls(self, file_name):
        data_xls = pd.read_excel(file_name, '1 курс (СПО)', index_col=None)
        arr_js = json.loads(data_xls.to_json())

        t1 = data_xls['Unnamed: 0'].tolist()
        t2 = data_xls['РАСПИСАНИЕ УЧЕБНЫХ ЗАНЯТИЙ И ПРОМЕЖУТОЧНОЙ АТТЕСТАЦИИ\nочно-заочного отделения'].tolist()
        group1 = data_xls['Unnamed: 4'].tolist()
        group2 = data_xls['Unnamed: 5'].tolist()

        days = []
        i = 0
        for d in t1:
            if i < 2:
                i += 1
                days.append(d)
                continue
            if str(d) != 'nan':
                day = str(d)
            days.append(day)

        i = 0
        times = []
        for d in t2:
            if i < 2:
                i += 1
                times.append(d)
                continue
            if str(d) != 'nan':
                time = str(d)
            times.append(time)

        pars = []
        flag = False
        for day, time, s1, s2 in zip(days, times, group1, group2):
            if flag:
                #classroom1 = s1[str(s1).find("(")+1:len(str(s1))-1]
                if str(s2) == 'nan':
                    pars.append(par1 + ";" + str(time) + ";" + str(s1))
                    pars.append(par2 + ";" + str(time) + ";" + str(s1))
                else:
                    #classroom2 = s2[str(s2).find("(") + 1:len(str(s2)) - 1]
                    pars.append(par1 + ";" + str(time) + ";" + str(s1))
                    pars.append(par2 + ";" + str(time) + ";" + str(s2))
                flag = False
                continue
            if str(s1).find('ПИ-20СВ') != -1 and str(s2).find('ПИ-20СВ') != -1:
                group_name1, group_name2 = s1,s2
                continue
            if str(s1).find('nan') != -1 and str(s2).find('nan') != -1:
                continue
            if str(s1).find('nan') == -1 and str(s2).find('nan') != -1:
                day = day[day.find('\n')+1:]
                par1 = str(day) + ";" + str(s1) + ";" + group_name1
                par2 = str(day) + ";" + str(s1) + ";" + group_name2
                flag = True
                continue
            if str(s1).find('nan') == -1 and str(s2).find('nan') == -1:
                day = day[day.find('\n') + 1:]
                par1 = str(day) + ";" + str(s1) + ";" + group_name1
                par2 = str(day) + ";" + str(s2) + ";" + group_name2
                flag = True
                continue

        pars_data = []
        date_now = datetime.now()
        for par in pars:
            par = par.split(';')
            date = par[0].split()
            month = self.RU_MONTH_VALUES[date[1]]
            if len(str(date[0])) != 1:
                str_date = str(date_now.year) + '-' + str(month) + '-' + str(date[0])
            else:
                str_date = str(date_now.year) + '-' + str(month) + '-' + '0' + str(date[0])
            pars_data.append(Pars(str_date, par[1], par[2], par[3], par[4]))

        return pars_data

    def download_files(self, urls):
        pars_data = []
        for url in urls:
            f = open(self.FILE_NAME, 'wb')
            ufr = requests.get(url)
            f.write(ufr.content)
            f.close()
            pars_data.append(self.__parse_xls(self.FILE_NAME))
        os.remove(self.FILE_NAME)
        return pars_data

    def get_urls(self, html):
        soup = BeautifulSoup(html.text, 'lxml')
        table = soup.find('div', class_='content__inner post__text')
        table = table.find_all('p', class_='text')

        flag = False
        urls = []
        for resp in table:
            if resp.text.find('Заочная форма обучения') != -1:
                break
            if resp.text.find('Очно-заочная форма обучения') != -1:
                flag = True
            if flag:
                try:
                    for cont in resp.contents:
                        if str(cont).find('link') != -1:
                            url = cont.attrs['href']
                            url = url[url.find('data')-1:]
                            urls.append(self.BASE_URL + url)
                            break
                except:
                    pass
        return urls

    @staticmethod
    def get_html(url):
        session = requests.session()
        response = session.post(url)
        return response
