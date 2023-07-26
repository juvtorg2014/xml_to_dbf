import pandas as pd
import itertools
from bs4 import BeautifulSoup as bs
import os
import dbf
import datetime

def xml_to_csv(name_file):
    with open(name_file, 'r', encoding='UTF-8') as f:
        content = f.read()

        # Извлечение содержания файла по спискам
        soup = bs(content, "xml")
        date_list = soup.find("ДатаПеречня").text.replace("-", "")
        name_csv = date_list + '.csv'
        full_name_csv = os.path.abspath(name_csv)
        ps_name = [values.text for values in soup.findAll('ФИО')]
        ps_date = [values.text.replace('-','.') for values in soup.findAll('ДатаРождения')]
        ps_seria = [values.text for values in soup.findAll('Серия')]
        ps_number = [values.text for values in soup.findAll('Номер')]
        ps_adress = [values.text for values in soup.findAll('ТекстАдреса')]
        ps_cr = [values.text for values in soup.findAll('Код')]
        ps_cn = [values.text for values in soup.findAll('Код')]

        # Собираем все списки в общую таблицу
        data = [item for item in itertools.zip_longest(ps_cr, ps_cn, ps_seria, ps_number, ps_name, ps_date, ps_adress)]
        df = pd.DataFrame(data=data)
        df.columns = ['KODCR', 'KODCN', 'SD', 'RG', 'NAMEU', 'GR', 'ADRESS']

        # Изменение даты в формат dd.mm.YY
        df['GR'] = pd.to_datetime(df['GR'], dayfirst=False)
        df['GR'] = df['GR'].dt.strftime('%d.%m.%Y')

        # Сохранение в файл
        if os.path.exists(full_name_csv):
            os.remove(full_name_csv)
        df.to_csv(full_name_csv, index=False, header=True, encoding='cp1251')
    return full_name_csv

def csv_to_dbf(name_file):
    dbf_file = name_file.replace('.csv', '.dbf')
    if os.path.exists(dbf_file):
        os.remove(dbf_file)

    table = dbf.Table(dbf_file,
                      'KODCR C(14); KODCN C(14); SD C(50); RG C(50); NAMEU C(250); GR D; ADRESS C(250)',
                      codepage='cp866')
    table.open(dbf.READ_WRITE)

    with open(name_file, 'r', encoding='cp1251') as f:
        while f.readline():
            new_line = []
            line = f.readline().split(',')
            if len(line) > 6:
                new_line.append(line[0]) # KODCR
                new_line.append(line[1]) # KODCN
                new_line.append(line[2]) # SD
                new_line.append(line[3]) # RG
                new_line.append(line[4].rstrip())

                if len(line[5]):
                    dd, mm, yy = line[5].split('.')
                    date_birth = datetime.datetime(int(yy), int(mm), int(dd))
                else:
                    date_birth= datetime.datetime(2000,1,1)
                new_line.append(date_birth)

                new_line.append(''.join(line[6:len(line)-1]).rstrip())
                table.append(tuple(new_line))
                print(date_birth)
            else:
                continue
    table.close()
    print(f"Создан файл {dbf_file}")


if __name__ == '__main__':
    #name_file = input('Введите имя файла без <xml>\n')
    # if not os.path.exists(os.path.abspath(name_file)):
    #     "Неправильное имя файла !!!"
    #     exit()
    name_file = xml_to_csv('20.07.2023.xml')
    csv_to_dbf(name_file)