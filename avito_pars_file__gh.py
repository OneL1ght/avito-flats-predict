
import requests
import pandas as pd
import time

from bs4 import BeautifulSoup
from csv import writer


HOST = 'https://www.avito.ru/'
URL = 'https://www.avito.ru/perm/kvartiry/prodam-ASgBAgICAUSSA8YQ?context=H4sIAAAAAAAA_0q0MrSqLraysFJKK8rPDUhMT1WyLrYyNLNSKk5NLErOcMsvyg3PTElPLVGyrgUEAAD__xf8iH4tAAAA&s=104'
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'
}
pages_link_part = '&p=2&s=104' # от изменения s ничего не меняется (зрительно)
                               # сами страницы в этом параметре &p=


def get_html(url):
    try:
        r = requests.get(url, headers=HEADERS)
    except ConnectionError:
        return None

    return r.text


def get_flats_links(page_link_url, HOST=HOST, to_exc=False):
    '''
    получает страницу с ссылками на квартиры
    выдает список ссылок
    (каждая из которых ведет на страницу
    отдельной квартиры)

    Функция использовалась в другом файле.
    Сначала были получены ссылки на все возможные
    квартиры, а после текущая программа проходила
    по каждой ссылке и тащила со страницы данные
    '''

    html = get_html(page_link_url)
    soup = BeautifulSoup(html, features='html.parser')
    # title_blocks = soup.find_all('div', class_='iva-item-titleStep-_CxvN') iva-item-titleStep-pdebR
    title_blocks = soup.find_all('div', class_='iva-item-titleStep-pdebR')

    links = [
        HOST+str(block.find('a').get('href'))[1:] for block in title_blocks
    ]

    if to_exc:
        data = pd.DataFrame(data=links, columns=['link'])
        data.to_excel('flats_links2.xlsx')

    return links


def extract_data_from_page(flat_url):
    '''
    применяется к каждой отдельной ссылке
    на страницу квартиры
    '''

    html = get_html(flat_url)

    if html == None:
        print('raise ConnectionErorr')
        time.sleep(15)
        return ['con_err' for _ in range(10)]

    soup = BeautifulSoup(html, features='html.parser')

    # if ad is closed
    if soup.find('a', class_='item-closed-warning'):
        return [None for _ in range(10)]

    row = []

    # title
    try:
        title = str(soup.find('span', class_='title-info-title-text').get_text())
    except AttributeError:
        title = None
    if title != None and '\xb2' in title:
        title = title.replace('\xb2', ' кв.')
    row.append(title)
    
    # price
    try:
        row.append(int(soup.find('span', class_='js-item-price').get('content')))
    except AttributeError:
        row.append(None)
    
    # addres
    try:
        row.append(
            ' '.join(str(soup.find('span', class_='item-address__string').get_text()).split())
        )
    except AttributeError:
        row.append(None)
    
    # from uls
    area = None
    rooms = None
    floors = None
    house_type = None
    constr_date = None
    ceiling_height = None

    lis = soup.find_all('li', class_='item-params-list-item')
    for li in lis:

        # area, rooms, floors --- about flat
        if li.find('span', class_='item-params-label').get_text() == 'Общая площадь: ':
            area = str(li.contents[2]).split()[0]
        if li.find('span', class_='item-params-label').get_text() == 'Количество комнат: ':
            rooms = str(li.contents[2]).split()[0]
        if li.find('span', class_='item-params-label').get_text() == 'Этаж: ':
            floors = ' '.join(str(li.contents[2]).split())

        # house type, date of construction
        if li.find('span', class_='item-params-label').get_text() == 'Тип дома: ':
            house_type = str(li.contents[2]).split()[0]
        if li.find('span', class_='item-params-label').get_text() == 'Год постройки: ':
            constr_date = str(li.contents[2]).split()[0]
        if li.find('span', class_='item-params-label').get_text() == 'Срок сдачи: ':
            constr_date = ' '.join(str(li.contents[2]).split())
        if li.find('span', class_='item-params-label').get_text() == 'Высота потолков: ':
            ceiling_height = str(li.contents[2]).split()[0]

    for i in [area, rooms, floors, house_type, constr_date, ceiling_height, flat_url]:
        row.append(i)

    return row


def write_file(links, out='test.txt'):
    ''' дописываем в файл '''

    with open(out, 'a') as f:
        for link in links:
            f.write(str(link) + '\n')




''' ВЫТЯГИВАЕМ ДАННЫЕ ДЛЯ CSV ЗАПИСИ В CSV ФАЙЛ'''

with open('2_88_1st_1000.txt', 'r') as f:

    i = 0
    for l in f:

        print(f'link {i}, zzz...')
        time.sleep(5.07) # timeout
        print()

        with open('avito_flats.csv', 'a', encoding='utf8', newline='') as flats_file:
            writer_object = writer(flats_file)

            writer_object.writerow(extract_data_from_page(l.rstrip()))

        i += 1
