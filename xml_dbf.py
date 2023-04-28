from bs4 import BeautifulSoup
import dbf as db
import os
import codecs

list_firm = {(""), (""), (""), (""), (""), (""), (""), ("")}

def create_dbf(date_file):
    new_table = db.Table(date_file + ".dbf",
            'NUMBER C(8); KODCR C(5); KODCN C(5); SD C(20); RG C(20); NAMEU C(200); ADRESS C(200); GR D',
            codepage='cp866')
    new_table.open(db.READ_WRITE)
    try:
        for n, item in enumerate(list_firm):
            if len(item) > 0:
                new_table.append(item)
                print(n, item[5])
    except IndexError:
        print(Exception)
    finally:
        new_table.close()


def xml_dbf(name):
    with open(name, 'r', encoding='utf-8') as fr:
        xml_file = fr.read()
        soup = BeautifulSoup(xml_file, 'xml')
        date_file = soup.find("ДатаПеречня").text.replace("-", "")
        nodes = soup.find('АктуальныйПеречень')
        subjects = nodes.find_all('Субъект')
        for n, node in enumerate(subjects):
            if node.find("ФЛ"):
                if node.find("ФИО"):
                    name = node.find("ФИО").text
                    names = name[:100] if len(name) > 100 else name
                    #names = name.encode().decode('cp866', errors='ignore')
                else:
                    name = ' '
                if node.find("ДатаРождения"):
                    date_birth = node.find("ДатаРождения").text
                    birth = db.Date(int(date_birth[:4]) , int(date_birth[5:7]), int(date_birth[8:]))
                else:
                    birth = db.Date(int('2000'), int("01"), int("01"))
                if node.find("Серия"):
                    series = node.find("Серия").text
                else:
                    series = ' '
                if node.find("Номер"):
                    number = node.find("Номер").text
                else:
                    number = ' '
                if node.find("ТекстАдреса"):
                    adres = node.find("ТекстАдреса").text
                    adress = adres[:100] if len(adres) > 100 else adres
                    #adress = adres.encode().decode('cp866', errors='ignore')
                else:
                    adress = " "
                if node.find("Код"):
                    code = node.find("Код").text
                else:
                     if node.find("Гражданство"):
                         if node.find("Гражданство").text == "РОССИЙСКАЯ ФЕДЕРАЦИЯ":
                             code = "843"
                     else:
                         code = ' '
                tuple_line = (str(n+1), code, code, series, number, names, adress, birth)
                print(tuple_line)
                list_firm.add(tuple_line)
            elif node.find("Орг"):
                if node.find("Орг").find("Наименование"):
                    name = node.find("Орг").find("Наименование").text
                    name = name[:100] if len(name) > 100 else name
                    names = name.encode().decode("cp866", errors='ignore')
                else:
                    name = ' '
                if node.find("Орг").find('ИНН'):
                    series = node.find("Орг").find('ИНН').text
                else:
                    series = ' '
                if node.find("Орг").find('ОГРН'):
                    number = node.find("Орг").find('ОГРН').text
                else:
                    number = ' '
                if node.find("ТекстАдреса"):
                    adres = node.find("ТекстАдреса").text
                    adres = adres[:100] if len(adres) > 100 else adres
                    adress = adres.encode().decode("cp866", errors='ignore')
                else:
                    adress = ' '
                if node.find("Страна"):
                    code = node.find("Страна").find("Код").text
                else:
                    code = ' '
                #tuple_line = (str(n + 1), code, code, series, number, names, adress)
                #list_firm.add(tuple_line)
    if os.path.exists(date_file):
        os.remove(date_file)
        create_dbf(date_file)
    else:
        create_dbf(date_file)


if __name__ == '__main__':
    xml_dbf('25.04.2023.xml')
