import os
import sys
import re
import subprocess
import importlib.util
from bs4 import BeautifulSoup
import lxml


def run_cmd(cmd):
    """ Запуск командной строки для установки пакетов"""
    ps = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True)
    print(ps.stdout)


def check_modules(module):
    """ Проверка модуля на наличие в системе"""
    if importlib.util.find_spec(module) is None:
        try:
            run_cmd(f'pip install {module}')
        except Exception as e:
            print(f"Не удалось установить пакет {module}", e)


def import_modules():
    check_modules('pandas')
    check_modules('bs4')
    check_modules('lxml')
    check_modules('dbf')
    check_modules('datetime')
    check_modules('itertools')


def xml_to_csv(name_file):
    import itertools
    import pandas as pd
    with open(name_file, 'r', encoding='UTF-8') as f:
        content = f.read()

        # Извлечение содержания файла по спискам
        soup = BeautifulSoup(content, 'xml')
        date_list = soup.find("ДатаПеречня").text.replace("-", "")
        csv_name = date_list + '.csv'
        full_name_csv = os.path.abspath(csv_name)
        ps_name = [values.text for values in soup.findAll('ФИО')]
        ps_date = [values.text.replace('-', '.') for values in soup.findAll('ДатаРождения')]
        ps_seria = [values.text for values in soup.findAll('Серия')]
        ps_number = [values.text for values in soup.findAll('Номер')]
        ps_adress = [values.text for values in soup.findAll('ТекстАдреса')]
        ps_cr = [values.text for values in soup.findAll('Код')]
        ps_cn = [values.text for values in soup.findAll('Код')]

        # Собираем все списки в общую таблицу
        # data = [item for item in itertools.zip_longest(ps_cr,ps_cn,ps_seria,ps_number,ps_name,ps_date,ps_adress)]
        data = []
        for item in itertools.zip_longest(ps_cr, ps_cn, ps_seria, ps_number, ps_name, ps_date, ps_adress):
            if item[4]:
                data.append(item)
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


def csv_to_dbf(file_name):
    import dbf
    import datetime
    dbf_file = file_name.replace('.csv', '.dbf')
    if os.path.exists(dbf_file):
        os.remove(dbf_file)

    table = dbf.Table(dbf_file,
                      'KODCR C(14); KODCN C(14); SD C(50); RG C(50); NAMEU C(250); GR D; ADRESS C(250)',
                      codepage='cp866')
    table.open(dbf.READ_WRITE)

    with open(file_name, 'r', encoding='cp1251') as f:
        while f.readline():
            new_line = []
            line = f.readline().split(',')
            if len(line) > 6:
                new_line.append(line[0])  # KODCR
                new_line.append(line[1])  # KODCN
                new_line.append(line[2])  # SD
                new_line.append(line[3])  # RG
                new_line.append(line[4].rstrip())  # NAMEU

                if len(line[5]):
                    patn = re.compile(r'\d{2}\W\d{2}\W\d{4}')
                    for i, item in enumerate(line):
                        if patn.findall(item):
                            dd, mm, yy = line[i].split('.')
                            date_birth = datetime.datetime(int(yy), int(mm), int(dd))
                else:
                    date_birth = datetime.datetime(2000, 1, 1)
                new_line.append(date_birth)

                new_line.append(''.join(line[6:len(line)-1]).rstrip())
                try:
                    table.append(tuple(new_line))
                except Exception as e:
                    print('Не загружается ', line[4])
                    print(e)
                    continue
                print(line[4], date_birth.date())
            else:
                continue
    table.close()
    print(f"Создан файл {dbf_file}")


if __name__ == '__main__':
    name = input('Введите имя файла без <xml>\n')
    if not os.path.exists(os.path.abspath(name + '.xml')):
        print(f"Неправильное имя файла {name} !!!")
        exit()
    run_cmd('pip install --upgrade pip')
    import_modules()
    csv_to_dbf(xml_to_csv(name + '.xml'))
