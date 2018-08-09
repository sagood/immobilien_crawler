import csv
import locale
from collections import namedtuple

from bs4 import BeautifulSoup
import requests

Info = namedtuple('Info', ['id', 'description', 'address', 'price', 'area', 'room_number', 'extra', 'href', 'viewed'])


def main():
    url = "https://www.immobilienscout24.de/Suche/S-T/Wohnung-Kauf/Nordrhein-Westfalen/Aachen/-/-/65,00-?enteredFrom=result_list"
    info_list = []
    retrieve(url, info_list)
    export_csv(info_list)


def export_csv(info_list):
    with open('flat.csv', 'w', encoding='utf-8-sig') as f:
        f_csv = csv.writer(f, dialect='excel')
        f_csv.writerow(Info._fields)
        f_csv.writerows(info_list)


def retrieve(url, info_list):
    page_prefix = 'https://www.immobilienscout24.de'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    request_list_items = soup.find('ul', attrs={'id': 'resultListItems'})
    flat_list = request_list_items.find_all('li', attrs={'class': 'result-list__listing'})
    for flat in flat_list:
        flat_id = flat['data-id']
        flat_title = flat.find('h5', attrs={'class': 'result-list-entry__brand-title'}).get_text()
        flat_href = flat.find('a')['href']
        flat_href = f'{page_prefix}/{flat_href}' if flat_href.startswith('/expose') else flat_href
        flat_address = flat.find('div', attrs={'class': 'result-list-entry__address'}) \
            .find('div', attrs={'class': 'font-ellipsis'}).get_text()

        flat_criterias = flat.find_all('dl', attrs={'class': 'result-list-entry__primary-criterion'})
        (flat_price, flat_area, flat_room_number) = map(lambda item: item.find('dd'), flat_criterias)
        flat_price = flat_price.get_text()
        try:
            locale.setlocale(locale.LC_ALL, 'de-DE')
            flat_price = str(int(locale.atof(flat_price[:-1]))) + '€'
        except ValueError as ex:
            pass

        flat_area = flat_area.get_text()
        flat_room_number = flat_room_number.find('span', attrs={'class': 'onlyLarge'})
        if flat_room_number is None:
            flat_room_number = "N/A"
        else:
            flat_room_number = flat_room_number.get_text()

        flat_secondary_criteria = flat.find('ul', attrs={'class': 'result-list-entry__secondary-criteria'})
        if flat_secondary_criteria is None:
            flat_secondary_criteria_text = "N/A"
        else:
            flat_secondary_criteria_text = str.join(', ', [item.get_text() for item in flat_secondary_criteria.find_all('li')])
        info = Info(id=flat_id, description=flat_title, href=flat_href, address=flat_address, price=flat_price,
                    area=flat_area, room_number=flat_room_number, extra=flat_secondary_criteria_text, viewed=False)
        info_list.append(info)

    next_page = soup.find('a', attrs={'data-nav-next-page': 'true'})
    if next_page is not None:
        new_url = page_prefix + next_page['href']
        retrieve(new_url, info_list)


if __name__ == '__main__':
    main()
