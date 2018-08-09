from bs4 import BeautifulSoup
import requests


def main():
    url = "https://www.immobilienscout24.de/Suche/S-T/Wohnung-Kauf/Nordrhein-Westfalen/Aachen/-/-/65,00-?enteredFrom=result_list"
    retrieve(url)


def retrieve(url):
    page_prefix = 'https://www.immobilienscout24.de'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    request_list_items = soup.find('ul', attrs={'id': 'resultListItems'})
    flat_list = request_list_items.find_all('li', attrs={'class': 'result-list__listing'})
    for flat in flat_list:
        flat_title = flat.find('h5', attrs={'class': 'result-list-entry__brand-title'}).get_text()
        flat_href = flat.find('a')['href']
        flat_href = f'{page_prefix}/{flat_href}' if flat_href.startswith('/expose') else flat_href
        flat_address = flat.find('div', attrs={'class': 'result-list-entry__address'}) \
            .find('div', attrs={'class': 'font-ellipsis'}).get_text()

        flat_criterias = flat.find_all('dl', attrs={'class': 'result-list-entry__primary-criterion'})
        (flat_price, flat_area, flat_room_number) = map(lambda item: item.find('dd'), flat_criterias)
        flat_price = flat_price.get_text()
        flat_area = flat_area.get_text()
        flat_room_number = flat_room_number.find('span', attrs={'class': 'onlyLarge'})
        if flat_room_number is None:
            flat_room_number = "N/A"
        else:
            flat_room_number = flat_room_number.get_text()

        flat_secondary_criteiras = flat.find('ul', attrs={'class': 'result-list-entry__secondary-criteria'})
        if flat_secondary_criteiras is None:
            flat_secondary_criteiras_text = "N/A"
        else:
            flat_secondary_criterias_text = str.join(', ', [item.get_text() for item in
                                                            flat_secondary_criteiras.find_all('li')])

    next_page = soup.find('a', attrs={'data-nav-next-page': 'true'})
    if next_page is not None:
        new_url = page_prefix + next_page['href']
        retrieve(new_url)


if __name__ == '__main__':
    main()
