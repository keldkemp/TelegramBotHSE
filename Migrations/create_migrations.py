"""
Генерация файла миграций
"""
import os
from os import walk

cwd = os.getcwd()
dir_path = os.path.dirname(os.path.realpath(__file__))
file_name = 'migrations_'

i = 1

for _, _, filenames in walk(dir_path):
    for file in filenames:
        if file == 'create_migrations.py':
            continue
        else:
            i += 1

fd = open(dir_path + '\\' + file_name + str(i) + '.json', 'w')
if i == 1:
    fd.write('{"commands": "", "file_name": "%s","migration_link": ""}' % (file_name + str(i)))
else:
    fd.write('{"commands": "","file_name": "%s","migration_link": "%s"}' % (file_name + str(i), file_name + str(i-1)))
fd.close()
