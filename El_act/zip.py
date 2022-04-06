import zipfile
import os

# os.chdir('Data')
with zipfile.ZipFile('res.zip', 'w') as my_zip_file:
    for file in os.listdir('Data'):
        my_zip_file.write(f'Data//{file}', file)
