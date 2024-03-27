import json
import re
from time import sleep

import requests
from bs4 import BeautifulSoup

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
}
url_metro = 'https://online.metro-cc.ru'
url_cheese = 'https://online.metro-cc.ru/category/molochnye-prodkuty-syry-i-yayca/syry?from=under_search'


def get_data():
    '''Функция парсинга данных с сайта metro в категории сыры.'''
    response = requests.get(url_cheese, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    last_number_page = soup.find_all(
        'a',
        class_='v-pagination__item catalog-paginate__item'
        )[-1].text

    for number_page in range(1, int(last_number_page) + 1):
        sleep(1)
        url_page = url_cheese + f'&page={number_page}'
        response = requests.get(url_page, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        all_publications = soup.find(id="products-inner")
        for product in all_publications:

            if product.find(
                   'p',
                   class_='product-title catalog-2-level-product-card__title style--catalog-2-level-product-card'
                   ):
                continue
            product_id = product.get('data-sku')
            product_url = url_metro + product.find(
                'a', class_='product-card-photo__link').get('href')
            response = requests.get(product_url, headers=headers)
            soup = BeautifulSoup(response.text, "lxml")
            product_name = soup.find(
                'h1',
                class_='product-page-content__product-name catalog-heading heading__h2'
                ).text.strip()
            characters = soup.find_all(
                'li', class_='product-attributes__list-item')

            for character in characters:
                if 'Бренд' in character.find(
                      'span', class_='product-attributes__list-item-name-text'
                       ).text:
                    product_brend = character.find(
                        'a',
                        class_='product-attributes__list-item-link reset-link active-blue-text'
                        ).text.strip()
                    break

            product_card_price = product.find(
                'div',
                class_='catalog-2-level-product-card__prices-rating'
                ).find_all('span', class_='product-price__sum-rubles')
            characters = soup.find(
                'div',
                class_='catalog-2-level-product-card__prices-rating')
            if len(product_card_price) == 2:
                regular_price = product_card_price[1].get_text()
                discount_price = product_card_price[0].get_text()
                regular_price = re.sub(r'\D', '', regular_price)
                discount_price = re.sub(r'\D', '', discount_price)
            else:
                regular_price = product_card_price[0].get_text()
                regular_price = re.sub(r'\D', '', regular_price)
                discount_price = 'Скидка отсутсвует'

            data = {
                'id товара из сайта': product_id,
                'наименование': product_name,
                'ссылка на товар': product_url,
                'регулярная цена': regular_price,
                'промо цена': discount_price,
                'бренд': product_brend
            }
            write_in_json_fite(data)
        print(f'Скрипт спарсил {number_page} стр. из {int(last_number_page)}')


def write_in_json_fite(new_data):
    '''Функция записи спрасеных данных в json файл'''
    array_for_json = []
    try:
        with open('result_parsing.json', 'r', encoding='utf-8') as file:
            array_for_json = json.load(file)
    except FileNotFoundError:
        pass
    array_for_json.append(new_data)
    with open('result_parsing.json', 'w', encoding='utf-8') as file:
        json.dump(array_for_json, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    get_data()
