from ftplib import FTP
import os
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import json
import paramiko
import datetime as dt
from dateutil import parser
import sql_f_xml

with open('config.json') as f:
    config = json.load(f)

FTP_WORK_DIR = config.get('FTP_WORK_DIR')
host = config.get('host')
user = config.get('user')
secret = config.get('secret')
port = config.get('port')
remote_path = config.get('remote_path')
START_DATE = parser.parse(config.get('START_DATE'))
NOW_DATE = dt.datetime.now()

to_do_transport = True

try:
    transport = paramiko.Transport((host, int(port)))
    transport.connect(username=user, password=secret)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print('Подключение к серверу приложений создано (для траспорта)')
except paramiko.ssh_exception.SSHException:
    to_do_transport = False
    print('Нет подключения к серверу приложений, транспорт не будет выполнен')

for folder in ['Temp', 'Data']:

    try:
        os.mkdir(folder)
    except FileExistsError:
        pass

    for path, folders, files in os.walk(folder):
        for file in files:
            os.unlink(os.path.join(path, file))

ftp = FTP('ftp.zakupki.gov.ru')
ftp.set_pasv(True)
ftp.login('free', 'free')

for subdir in ['currMonth', 'prevMonth']:

    all_files_data = []
    ftp.dir(f'{FTP_WORK_DIR}//{subdir}//', all_files_data.append)
    for file_data in all_files_data:

        file_tokens = file_data.split()
        name = file_tokens[-1]
        file_date_str = file_tokens[5] + ' ' + file_tokens[6] + ' ' + file_tokens[7]
        file_date = parser.parse(file_date_str)

        if file_date >= START_DATE:
            print(f'В процессе: {name} от {file_date}')
            with open(f'Temp//{name}', 'wb') as f:
                ftp.retrbinary('RETR ' + f'{FTP_WORK_DIR}//{subdir}//{name}', f.write)

            z = ZipFile(f'Temp//{name}')
            for item in z.namelist():
                if item.startswith('contractProcedure_') and item.endswith('.xml'):
                    z.extract(item, 'Data')
                    tree = ET.parse(f'Data//{item}')
                    root = tree.getroot()
                    isEDIBased = '{http://zakupki.gov.ru/oos/types/1}isEDIBased'
                    if root.find(f'.//{isEDIBased}').text == 'false':
                        os.unlink(f'Data//{item}')
                    # else:
                    #     if to_do_transport:
                    #         print(f'Транспортирую {item} на сервер приложений...', end='')
                    #         sftp.put(f'Data//{item}', f'{remote_path}//{item}')
                    #         print(' Успешно')
if to_do_transport:
    sftp.close()
    print('Подключение к серверу приложений закрыто')

ftp.close()

config['START_DATE'] = NOW_DATE.strftime('%Y%m%d%H%M%S')

with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

with ZipFile('res.zip', 'w') as my_zip_file:
    for file in os.listdir('Data'):
        my_zip_file.write(f'Data//{file}', file)

print('Архив готов!')

sql_f_xml.get_sql()
print('Скрипты готовы')
