import xml.etree.ElementTree as ET
import os


def get_sql():

    with open('scripts.sql', 'w', encoding='CP1251') as f:
        f.write('')

    id_ = '{http://zakupki.gov.ru/oos/types/1}id'
    versionNumber = '{http://zakupki.gov.ru/oos/types/1}versionNumber'
    sid = '{http://zakupki.gov.ru/oos/types/1}sid'
    documentNum = '{http://zakupki.gov.ru/oos/types/1}documentNum'
    fulfilmentSum = '{http://zakupki.gov.ru/oos/types/1}fulfilmentSum'

    for file in os.listdir('Data'):
        tree = ET.parse(f'Data//{file}')
        root = tree.getroot()
        # print(root.find(f'.//{id_}').text)
        eisuid = root.find(f'.//{id_}').text
        version = root.find(f'.//{versionNumber}').text
        eisid = root.find(f'.//{sid}').text
        executiondocumentno  = root.find(f'.//{documentNum}').text

        if root.find(f'.//{fulfilmentSum}') != None:
            executionamount = root.find(f'.//{fulfilmentSum}').text
            executionamount_text = f"executionamount = '{executionamount}'"
        else:
            executionamount_text = "executionamount is null"
        # executionamount = '{executionamount}'

        print(file)
        print(f'''update rcs_obligationexecution set eisid = '{eisid}' where executiondocumentno = '{executiondocumentno}' and {executionamount_text} and eisid is null
	and id = (select obligationexecutionid from rcs_contractexecution_obligationexecutions where contractexecutionid = (select id from rcs_contractexecution where
																													   eisuid = '{eisuid}' and version = {version}));''')
        with open('scripts.sql', 'a', encoding='CP1251') as f:
            f.write(f'--{file}\n')
            f.write(f'''update rcs_obligationexecution set eisid = '{eisid}' where executiondocumentno = '{executiondocumentno}' and {executionamount_text} and eisid is null
	and id = (select obligationexecutionid from rcs_contractexecution_obligationexecutions where contractexecutionid = (select id from rcs_contractexecution where
																													   eisuid = '{eisuid}' and version = {version}));\n''')


if __name__ == '__main__':
    get_sql()
