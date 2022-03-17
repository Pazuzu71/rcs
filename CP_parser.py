import os
import xml.etree.ElementTree as ET

work_dir = os.getcwd()
try:
    os.mkdir(os.path.join(work_dir, 'contractProcedure'))
except FileExistsError:
    pass

with open('scripts.sql', 'w') as f:
    f.write('')

if os.getcwd() != os.path.join(work_dir, 'contractProcedure'):
    os.chdir('contractProcedure')

for file in os.listdir():
    tree = ET.parse(file)
    root = tree.getroot()
    # elemList = []
    # for el in tree.iter():
    #     elemList.append(el.tag)
    # print(*elemList, sep='\n')
    contractProcedure = '{http://zakupki.gov.ru/oos/export/1}contractProcedure'
    executions = '{http://zakupki.gov.ru/oos/types/1}executions'
    execution = '{http://zakupki.gov.ru/oos/types/1}execution'
    docAcceptance = '{http://zakupki.gov.ru/oos/types/1}docAcceptance'
    sid = '{http://zakupki.gov.ru/oos/types/1}sid'
    documentNum = '{http://zakupki.gov.ru/oos/types/1}documentNum'
    for child in root.findall(f'{contractProcedure}/{executions}/{execution}/{docAcceptance}'):
        # print(child.find(sid).text)
        with open(work_dir + '/scripts.sql', 'a', encoding='CP1251') as f:
            f.write(f"UPDATE public.rcs_obligationexecution SET eisid='{child.find(sid).text}', firstversionid=null WHERE executiondocumentno='{child.find(documentNum).text}' and version != 0;" + '\n')

    for child in root.findall(f'.//{docAcceptance}'):
        print(child.find(sid).text)
