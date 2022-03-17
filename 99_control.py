import os
from ftplib import FTP
import datetime as dt
from dateutil import parser
import zipfile
import json


def create_dir(dir_name):

    if os.getcwd() != WORK_DIR:
        os.chdir(WORK_DIR)
    try:
        os.mkdir(dir_name)
    except FileExistsError:
        pass


def change_dir(dir_name):
    if os.getcwd() != os.path.join(WORK_DIR, dir_name):
        return os.chdir(os.path.join(WORK_DIR, dir_name))


def is_empty_dir(dir_name):
    for path, dirs, files in os.walk(os.path.join(WORK_DIR, dir_name)):
        for file in files:
            os.unlink(os.path.join(path, file))


def get_zips():

    ftp_dirs = ['contracts', 'notifications', 'plangraphs2020']

    ftp = FTP('ftp.zakupki.gov.ru')
    ftp.set_pasv(True)
    ftp.login('free', 'free')
    ftp.cwd(FTP_WORK_DIR)
    change_dir('Temp')
    for ftp_dir in ftp_dirs:
        for folder in ['currMonth', 'prevMonth']:
            zips = list()
            ftp.cwd('//'.join([FTP_WORK_DIR, ftp_dir, folder]))
            ftp.dir(zips.append)
            for zippy in zips:
                tokkens = zippy.split()
                date_file_str = tokkens[5] + " " + tokkens[6] + " " + tokkens[7]
                date_file = parser.parse(date_file_str)
                name = tokkens[8]
                if parser.parse(END_DATE) >= date_file >= parser.parse(START_DATE):
                    with open(ftp_dir + '_' + name, 'wb') as f:
                        ftp.retrbinary('RETR ' + name, f.write)
    ftp.close()


def main():
    create_dir('Temp')
    create_dir('Result')
    is_empty_dir('Temp')
    is_empty_dir('Result')
    get_zips()

    for item in os.listdir():
        z = zipfile.ZipFile(item)
        for xml in z.namelist():
            if xml.endswith('.xml'):
                z.extract(xml, os.path.join(WORK_DIR, 'Result'))
    os.chdir(os.path.join(WORK_DIR, 'Result'))
    if 'res.zip' in os.listdir():
        os.unlink(os.path.join(WORK_DIR, 'res.zip'))
    with zipfile.ZipFile(os.path.join(WORK_DIR, 'res.zip'), 'w') as my_zip_file:
        for file in os.listdir():
            my_zip_file.write(file)

    print('Можно забирать')
    # is_empty_dir('Temp')
    # is_empty_dir('Result')



# config = {
#     'FTP_WORK_DIR': '//fcs_regions//Tulskaja_obl//control99docs',
#     'START_DATE': '20220317110000',
#     'END_DATE': '20220331000000',
# }

WORK_DIR = os.getcwd()
DATE_NOW = dt.datetime.now().strftime('%Y%m%d%H%M%S')

with open(os.path.join(WORK_DIR, 'config.json')) as f:
    config = json.load(f)

FTP_WORK_DIR = config.get('FTP_WORK_DIR')
START_DATE = config.get('START_DATE')
END_DATE = config.get('END_DATE')


if __name__ == '__main__':
    main()

    config['START_DATE'] = DATE_NOW

    with open(os.path.join(WORK_DIR, 'config.json'), 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
