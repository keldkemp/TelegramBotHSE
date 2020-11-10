"""
Пока что бесполезный файл. Можно удалить
"""
from DB.DataBasePG import DataBasePg


db = DataBasePg()
list = db.get_stat()
list_date = []
list_req = []
for ls in list:
    list_date.append(ls[1])
    list_req.append(ls[0])
