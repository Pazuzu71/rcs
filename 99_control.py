import os
from ftplib import FTP
from dateutil import parser
import zipfile


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
    for path, dirs, files in os.walk(dir_name):
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
        zips = list()
        ftp.cwd('//'.join([FTP_WORK_DIR, ftp_dir, 'currMonth']))
        ftp.dir(zips.append)
        for zippy in zips:
            tokkens = zippy.split()
            name = tokkens[8]
            tokkens = name.split('_')
            date_in_name = tokkens[3]
            if parser.parse(date_in_name) >= parser.parse(START_DATE):
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


WORK_DIR = os.getcwd()
FTP_WORK_DIR = '//fcs_regions//Tulskaja_obl//control99docs'
START_DATE = '20220219120000'

if __name__ == '__main__':
    main()
