from http.server import HTTPServer, SimpleHTTPRequestHandler
import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_age_of_winery():
    winery_opening_date = datetime.datetime(1920, 1, 1)
    current_date = datetime.datetime.today()
    return current_date.year - winery_opening_date.year


def write_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(data)
    return file


def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8-sig') as handler:
        file = handler.read()
    return file


def translate_key(key):
    translation_of_keys = {
        'Название': 'title',
        'Сорт': 'variety',
        'Картинка': 'image',
        'Цена': 'price'
    }
    return translation_of_keys[key]


def get_key_and_value(string):
    if string == 'Выгодное предложение':
        return 'sale', True
    key, value = string.split(':')
    key = translate_key(key)
    value = value.strip()
    return key, value


def get_group_of_products(raw_product_info):
    list_of_data_on_products = raw_product_info.split('\n')
    group_of_products = []
    product_details = []

    for number, data in enumerate(list_of_data_on_products):
        if data:
            product_details.append(data)
            if number != len(list_of_data_on_products) - 1:
                continue

        product_info = dict([
            (get_key_and_value(item))
            for item in product_details
        ])

        if not product_info.get('sale'):
            product_info.update({'sale': False})

        group_of_products.append(product_info)
        product_details = []

    return group_of_products


def get_list_of_product_groups(info_about_products):
    list_of_data_on_products = info_about_products.split('\n\n\n')
    list_of_product_groups = []
    group_title = str()

    for item in list_of_data_on_products:
        if item.startswith('#'):
            group_title = item.strip('# ')
        else:
            group_of_products = get_group_of_products(item)
            list_of_product_groups.append(
                {group_title: group_of_products}
            )

    return list_of_product_groups


def fetch_template(filepath, template_name):
    env = Environment(
        loader=FileSystemLoader(filepath),
        autoescape=select_autoescape(['html'])
    )
    return env.get_template(template_name)


def render_template(template, winery_age, list_of_product_groups):
    rendered_page = template.render(
        winery_age=winery_age,
        list_of_product_groups=list_of_product_groups
    )
    write_file('index.html', rendered_page)


def run_server():
    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()
    return server


if __name__ == '__main__':
    template_for_rendering = fetch_template('.', 'template.html')
    winery_age = get_age_of_winery()
    products_info = read_file('wine.txt')
    list_of_product_groups = get_list_of_product_groups(products_info)
    render_template(
        template_for_rendering,
        winery_age,
        list_of_product_groups
    )
    server = run_server()
