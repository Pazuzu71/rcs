import requests
import os
import xml.etree.ElementTree as ET
import re
import base64


wsdl = "https://int44.zakupki.gov.ru/eis-integration/elact/customer-docs?wsdl"

regNum = '03186000028'
contractRegNum = '3235001366622000009'
usertoken = ''


headers = {
    "usertoken": usertoken
}

data = f'''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:elac="http://zakupki.gov.ru/eruz/ws/elacts">
   <!--<soapenv:Header/>-->
   <soapenv:Body>
      <elac:lkzGetObjectListRequest>
         <elac:sender>
            <elac:regNum>{regNum}</elac:regNum>
         </elac:sender>
         <elac:customer>
            <elac:regNum>{regNum}</elac:regNum>
         </elac:customer>
         <elac:contractRegNum>{contractRegNum}</elac:contractRegNum>
      </elac:lkzGetObjectListRequest>
   </soapenv:Body>
</soapenv:Envelope>
'''

req = requests.post(url=wsdl, data=data, headers=headers)
# print(req.text)
src = req.text

try:
    os.mkdir(f'{contractRegNum}')
except Exception as ex:
    pass

with open(f'{contractRegNum}//lkzGetObjectList.xml', 'w') as f:
    f.write(src)

tree = ET.parse(f'{contractRegNum}//lkzGetObjectList.xml')
root = tree.getroot()
objectInfo = '{http://zakupki.gov.ru/eruz/ws/elacts}objectInfo'
id_ = '{http://zakupki.gov.ru/eruz/ws/elacts}id'
objectId = '{http://zakupki.gov.ru/eruz/ws/elacts}objectId'
documentKind = '{http://zakupki.gov.ru/eruz/ws/elacts}documentKind'
documentDate = '{http://zakupki.gov.ru/eruz/ws/elacts}documentDate'
versionNumber = '{http://zakupki.gov.ru/eruz/ws/elacts}versionNumber'
status = '{http://zakupki.gov.ru/eruz/ws/elacts}status'
objectList = root.findall(f'.//{objectInfo}')
objectIdList = []

for objectInfo in objectList:
    if objectInfo.find(documentKind).text == 'ON_NSCHFDOPPR':
        objectIdList.append({objectInfo.find(id_).text: [objectInfo.find(objectId).text, objectInfo.find(documentDate).text,
                                                         objectInfo.find(versionNumber).text, objectInfo.find(status).text]})

# elemList = []
# for el in tree.iter():
#     elemList.append(el.tag)
#
# print(elemList)
# print(objectList)
print(objectIdList)

for objectId_dict in objectIdList:
    for k, v in objectId_dict.items():
        objectId = v[0]
        documentDate = v[1]
        versionNumber = v[2]
        status = v[3]
        data = f'''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:elac="http://zakupki.gov.ru/eruz/ws/elacts">
           <soapenv:Header/>
           <soapenv:Body>
              <elac:lkzGetObjectInfoRequest>
                 <elac:sender>
                    <elac:regNum>{regNum}</elac:regNum>
                 </elac:sender>
                 <elac:customer>
                    <elac:regNum>{regNum}</elac:regNum>
                 </elac:customer>
                 <elac:documentUid>{objectId}</elac:documentUid>
                 <elac:documentKind>ON_NSCHFDOPPR</elac:documentKind>
              </elac:lkzGetObjectInfoRequest>
           </soapenv:Body>
        </soapenv:Envelope>
        '''

        req = requests.post(url=wsdl, data=data, headers=headers)
        src = req.text
        with open(f'{contractRegNum}//{objectId}_{versionNumber}_{status}.xml', 'w') as f:
            f.write(src)
        with open(f'{contractRegNum}//{objectId}_{versionNumber}_{status}.xml') as f:
            src = f.read()
        pattern = r'<Контент>.*?</Контент>'
        document_and_appendix = []
        for _ in re.findall(pattern, src):
            _ = _.replace('<Контент>', '').replace('</Контент>', '').strip()
            decoded_data = base64.b64decode(_)
            document_and_appendix.append(decoded_data.decode('cp1251'))

        with open(f'{contractRegNum}//{objectId}_{versionNumber}_{status}_Документ.xml', 'w', encoding='utf-8') as f:
            f.write(document_and_appendix[0])

        with open(f'{contractRegNum}//{objectId}_{versionNumber}_{status}_Прилож.xml', 'w') as f:
            f.write(document_and_appendix[1])
