from ftplib import FTP
import json
from datetime import datetime
from dateutil import parser
import os
import zipfile
import xml.etree.ElementTree as ET

'''Сохраняем время запуска в Date_now'''
Date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# print(Date_now,type(Date_now))
'''Получаем рабочую папку'''
Work_dir = os.getcwd()
# print(os.path.join(work_dir,'Temp'))


'''Проверяем наличие в текущем каталоге временной папки и если такой нет - создаем'''
try:
    os.mkdir('Temp')
except FileExistsError:
    pass
'''Проверяем наличие файлов во временной папке, если есть - удаляем'''
for path, dirs, files in os.walk('Temp'):
    for file in files:
        os.unlink(os.path.join(path, file))
'''Загружаем в словарь конфиг из джсончика'''
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
'''Берем из конфига дату последнего запуска'''
Last_run_time = parser.parse(config['Last_run_time'])

'''------------------------------------'''
'''Подключаемся к ФТП ЕИС'''
ftp = FTP('ftp.zakupki.gov.ru')
ftp.login('free', 'free')
# Меняем рабочую папку на ФТП
# ftp.cwd('fcs_regions//Tulskaja_obl//contracts//currMonth')
ftp.cwd('fcs_regions//Tulskaja_obl//contracts//prevMonth')
# Создаем список файлов и их имен из рабочей папки ФТП ЕИС
xmls, names = list(), list()
ftp.dir(xmls.append)
for xml in xmls:
    tokens = xml.split()
    name = tokens[8]
    names.append(name)
    time_str = tokens[5] + " " + tokens[6] + " " + tokens[7]
    time = parser.parse(time_str)
    if os.getcwd() != os.path.join(Work_dir, 'Temp'):
        os.chdir('Temp')
    # Загружаем только то, что после последнего запуска
    # Проверить UTC!!!
    if time > Last_run_time:
        with open(name, 'wb') as f:
            ftp.retrbinary('RETR ' + name, f.write)
ftp.close()
'''Распаковываем всё во временную папку'''
for name in names:
    if zipfile.is_zipfile(name):
        z = zipfile.ZipFile(name, 'r')
        z.extractall()
'''Удаляем всё лишнее'''
for item in os.listdir(os.path.join(Work_dir, 'Temp')):
    if not item.endswith('.xml') or not item.startswith('contractProcedure'):
        os.unlink(os.path.join(Work_dir, 'Temp', item))
    elif item.startswith('contractProcedureCancel'):
        os.unlink(os.path.join(Work_dir, 'Temp', item))
    else:
        tree = ET.parse(item)
        root = tree.getroot()
        subroot = '{http://zakupki.gov.ru/oos/export/1}contractProcedure'
        isEDIBased = '{http://zakupki.gov.ru/oos/types/1}isEDIBased'
        for child in root.findall(subroot + '/' + isEDIBased):
            if child.text == 'false':
                os.unlink(os.path.join(Work_dir, 'Temp', item))
