import random

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random

url = 'https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie'  #ссылка на нашу страницу

#____________возвращаем результат работы метода get библиотеки requests (парсим код страницы)________________

headers = {      # заголовки
'Access-Control-Allow-Origin':'*',

'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43'
}
reg = requests.get(url, headers=headers)    # url к которому мы обращаемся и заголовки
src = reg.text
#print(src)

with open('index.html', 'w', encoding='utf-8') as file: # сохраняем код страницы в файл
    file.write(src)

with open('index.html', encoding='utf-8') as file:  # откроем, прочитаем наш файл и сохраним в переменную
    src1 = file.read
soup = BeautifulSoup(src, 'lxml')    # зададим обьекту soup в качестве параметров: переменную src, парсер lxml
all_product = soup.find_all(class_='mzr-tc-group-item-href') #собираем ссылки

all_categories_dict = {}    #создаем словарь для наших данных
for item in all_product:
    item_text = item.text   # Название
    item_href = 'https://health-diet.ru' + item.get('href')    # ссылка
    #print(f'{item_text}: {item_href}')
    all_categories_dict[item_text] = item_href    #наполняем словарь на каждой итерации цикла (ключи - имена, значения - ссылки)
with open('all_categories_dict.json', 'w', encoding='utf-8') as file:  #сохраняем данные в json файл
    json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)  #стандартные параметры для json

with open('all_categories_dict.json', encoding='utf-8') as file:  #загрузим наш json файл со всей информацией в перемнную
    all_categories = json.load(file)
#print(all_categories)

#заходим циклом на каждой итерации которого будем заходить на нову страницу категории и собирать данные о товарах и хим. состав.

iteration_count = int(len(all_categories)) - 1      #для пустой страницы Danone
count = 0   #создаем счетчик для того чтобы добавлять к имени файла
print(f'Всего итераций: {iteration_count}')

for category_name, category_href in all_categories.items():


    rep = [',', ' ', ',', '-', "'"]
    for itemm in rep:
        if itemm in category_name:
            category_name = category_name.replace(itemm, '_')
    print(category_name)

    reg1 = requests.get(url=category_href, headers=headers)  # обращаемся к страницам
    src2 = reg1.text    #сохраняем ссылки в переменную

    with open(f'data/{count}_{category_name}.html', 'w', encoding='utf-8') as file:   #сохраняем страницу под именем категории (data/ - сохраняем в папку DATA которую просто создали)
        file.write(src2)
    with open(f'data/{count}_{category_name}.html', encoding='utf-8') as file:    #откроем и сохраним код страницы в переменную
        src3 = file.read()
    soup = BeautifulSoup(src3, 'lxml')

    #проверим страницы на наличие таблицы с продуктами
    # alert_block = soup.find('uk-alert-danger')
    # if alert_block is not None:
    #     continue

    try:
        # Блок кода, который может вызвать ошибку
        table_head = soup.find(class_='mzr-tc-group-table').find('tr').find_all('th')
        # Остальной код для обработки заголовков и продуктов
    except AttributeError:
        # Блок кода, который выполняется при возникновении ошибки AttributeError
        print(f"Таблица не найдена на странице: {category_name}")
        continue

    table_head = soup.find(class_='mzr-tc-group-table').find('tr').find_all('th')   #собираем заголовки таблицы (продукты, БЖУ)
    # print(table_head)
    product = table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbohydrates = table_head[4].text
    # print(fats)



    with open(f'data/{count}_{category_name}.csv', 'w', encoding="utf-8-sig") as file:   #открываем файл на запись с расширением csv
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            [
                product,
                calories,
                proteins,
                fats,
                carbohydrates
            ]
        )

    products_data = soup.find(class_='mzr-tc-group-table').find('tbody').find_all('tr')  #собираем данные продуктов
    product_info = []
    for item in products_data:
        product_tds = item.find_all('td')

        title = product_tds[0].find('a').text
        calories = product_tds[1].text
        proteins = product_tds[2].text
        fats = product_tds[3].text
        carbohydrates = product_tds[4].text
        # print(title)
        # print(proteins)

        product_info.append(             #создадим словарь который запишем в json  файл
            {
                'title': title,
                'calories': calories,
                'proteins': proteins,
                'fats': fats,
                'carbohydrates': carbohydrates

            }
        )

        with open(f'data/{count}_{category_name}.csv', 'a', newline='', encoding="utf-8-sig") as file:  # открываем файл на запись с расширением csv
            writer = csv.writer(file, delimiter=';')
            writer.writerow(
                [
                    title,
                    calories,
                    proteins,
                    fats,
                    carbohydrates
                ]
            )

    with open(f'data/{count}_{category_name}.json', 'a', encoding="utf-8-sig") as file:              #Запишем словарь в созданный json файл
        json.dump(product_info, file, indent=4, ensure_ascii=False)

    count += 1
    print(f'# Итерация {count}. {category_name} записан...')
    iteration_count = iteration_count - 1

    if iteration_count == 0:
        print('Работа завершена')
        break                                             #выходим из цикла

    print(f'Осталось итераций: {iteration_count}')
    time.sleep(random.randrange(2, 4))
