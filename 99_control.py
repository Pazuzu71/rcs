import os
from ftplib import FTP


def temp(WORK_DIR):
    if os.getcwd() != WORK_DIR:
        os.chdir(WORK_DIR)
    try:
        os.mkdir('Temp')
    except FileExistsError:
        pass


def main():
    temp(WORK_DIR)


WORK_DIR = os.getcwd()

if __name__ == '__main__':
    main()
