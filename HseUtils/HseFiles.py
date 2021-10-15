"""
Класс в основном нужен для работы с сайтом HSE.
Сейчас здесь происходит основной движ по расписанию
"""
import requests
import pandas as pd
import os
import xlrd
from bs4 import BeautifulSoup
from datetime import datetime
from models.Models import Pars


class HSE:
    BASE_URL = 'https://perm.hse.ru'
    FILE_NAME = 'file_test.xls'
    NEW_FILE_NAME = 'file_test.xlsx'
    SHEET_NAME = '1 курс (СПО)'
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
    SHEETS = {
        'A': 1,
        'B': 2,
        'C': 3,
        'D': 4,
        'E': 5,
        'F': 6,
        'G': 7,
        'H': 8,
        'I': 9,
    }

    def read_excel(self, path):
        if path.endswith('xlsx'):
            excel = pd.ExcelFile(xlrd.open_workbook(path), engine='xlrd')
        elif path.endswith('xls'):
            excel = pd.ExcelFile(xlrd.open_workbook(path, formatting_info=True), engine='xlrd')
        else:
            raise ValueError("Could not read this type of data")
        return excel

    def parse_excel(self, excel_file, sheet_name):
        sheet = excel_file.book.sheet_by_name(sheet_name)
        df = excel_file.parse(sheet_name=sheet_name, header=None)
        return sheet, df

    def fill_merged_na(self, sheet, dataframe):
        for e in sheet.merged_cells:
            rl, rh, cl, ch = e
            base_value = sheet.cell_value(rl, cl)
            dataframe.iloc[rl:rh, cl:ch] = base_value
        return dataframe

    def __get_days(self, t1: list) -> list:
        days = []
        i = 0
        for d in t1:
            if isinstance(d, datetime):
                continue
            if i < 2:
                i += 1
                days.append(d)
                continue
            if str(d) != 'nan':
                day = str(d)
            days.append(day)

        return days

    def __get_times(self, t2: list) -> list:
        times = []
        i = 0
        for d in t2:
            if i < 2:
                i += 1
                times.append(d)
                continue
            if str(d) != 'nan':
                time = str(d)
            times.append(time)

        return times

    def __get_pars(self, days: list, times: list, group1: list) -> list:
        pars = []
        flag = False
        i = 0
        for day, time, s1 in zip(days, times, group1):
            i += 1
            if flag:
                day = day[day.find('\n') + 1:] + ';'
                if s1 == par1.replace(day, '').replace(';' + group_name1, ''):
                    pars.append(par1 + ";" + str(time) + ";None")
                else:
                    pars.append(par1 + ";" + str(time) + ";" + str(s1))
                flag = False
                continue
            if str(s1).find('подразделения') != -1 or str(s1).find('РАСПИСАНИЕ УЧЕБНЫХ') != -1:
                continue
            if str(s1).find('учебного года') != -1:
                continue
            if i == 2:
                group_name1 = s1
                continue
            if str(s1).find('nan') != -1:
                if isinstance(day, int):
                    continue
                if str(pars).find(str(day[day.find('\n') + 1:])) == -1:
                    pars.append(day[day.find('\n') + 1:] + ';None;None;None;None')
                continue
            if str(s1).find('nan') == -1 and str(s1) != '':
                day = day[day.find('\n') + 1:]
                par1 = str(day) + ";" + str(s1) + ";" + group_name1
                flag = True
                continue

        return pars

    def __get_pars_data(self, pars: list) -> list:
        pars_data = []
        date_now = datetime.now()
        for par in pars:
            par = par.split(';')
            date = par[0].split()
            month = self.RU_MONTH_VALUES[date[1]]
            year = date_now.year
            if month == '01' and date_now.month == 12:
                year += 1
            if len(str(date[0])) != 1:
                str_date = str(year) + '-' + str(month) + '-' + str(date[0])
            else:
                str_date = str(year) + '-' + str(month) + '-' + '0' + str(date[0])
            pars_data.append(Pars(str_date, par[1], par[2], par[3], par[4]))

        return pars_data

    def __parse_xls(self, file_name: str) -> list:
        excel = self.read_excel(file_name)
        sheets = excel.sheet_names
        pars_data = []

        for sheet in sheets:
            _sheet, _excel = self.parse_excel(excel, sheet)
            dt = self.fill_merged_na(_sheet, _excel)
            data_xls = pd.read_excel(file_name, sheet, index_col=None)

            # 0 - всегда дни, 1 - всегда время. Остальные в списке - это группы
            head_column = list(data_xls.columns)

            t1 = data_xls[head_column[0]].tolist()
            t2 = data_xls[head_column[1]].tolist()
            head_column.pop(0)
            head_column.pop(0)
            groups = []
            indx = 1

            for col_name in head_column:
                indx += 1
                group = dt[indx].tolist()
                group.pop(0)

                if str(group[1]) == 'nan':
                    continue

                if group[1] in groups:
                    continue
                groups.append(group[1])

                days = self.__get_days(t1)
                times = self.__get_times(t2)
                pars = self.__get_pars(days=days, times=times, group1=group)
                pars_data.append(self.__get_pars_data(pars))

        return pars_data

    def download_files(self, urls: list) -> list:
        pars_data = []
        for url in urls:
            f = open(self.FILE_NAME, 'wb')
            ufr = requests.get(url)
            f.write(ufr.content)
            f.close()
            pars_data.append(self.__parse_xls(self.FILE_NAME))
        os.remove(self.FILE_NAME)
        return pars_data

    def get_urls(self, html) -> list:
        soup = BeautifulSoup(html.text, 'lxml')
        table = soup.find('div', class_='content__inner post__text')
        table = table.find_all('p', class_='text')

        flag = False
        flag_2 = False
        urls = []
        for resp in table:
            if resp.text.find('Заочная форма обучения') != -1:
                break
            if resp.text.find('Бакалавриат') != -1:
                #flag_2 = True
                pass
                #TODO: Очники
            if resp.text.find('Очно-заочная форма обучения') != -1:
                flag = True
            if flag_2:
                try:
                    for cont in resp.contents:
                        if str(cont).find('link') != -1 and cont.text.find('изм') != -1:
                            url = cont.attrs['href']
                            url = url[url.find('data') - 1:]
                            urls.append(self.BASE_URL + url)
                            flag_2 = False
                            break
                except:
                    pass
            if flag:
                try:
                    for cont in resp.contents:
                        if str(cont).find('link') != -1:
                            url = cont.attrs['href']
                            url = url[url.find('data') - 1:]
                            urls.append(self.BASE_URL + url)
                            break
                except:
                    pass
        return urls

    @staticmethod
    def get_html(url: str):
        session = requests.session()
        response = session.post(url)
        return response
