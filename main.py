### Здесь ТГ-бот + моделька
import os
from dotenv import load_dotenv
import telebot
import json
import numpy as np
import pandas as pd
from telebot import types
import pickle

# Загрузка модели
with open('model.pkl', 'rb') as file:
    model = pickle.load(file)

load_dotenv()
token = os.getenv('TOKEN')
bot = telebot.TeleBot(token)

# /start - Приветствие пользователя
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton('/help')
    btn2 = types.KeyboardButton('/params')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id,
f"Доброго времени суток {message.from_user.username} 👋, здесь вы сможете узнать примерную стоимость жилья \
в городе Санкт-Петербург 🌆, задав необходимые параметры \n\n<em>Чтобы детальней узнать о работе воспользуйтесь командой:</em> <b>/help</b>",
                     parse_mode = 'html',
                     reply_markup=markup)

# /help - Команда для отображения помощи
@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id,
f"Для предзакания вам нужно ввести следующие желаемые параметры:\n\n\
\t1. Общая площадь\n\
\t2. Район\n\
\t3. Метро\n\
\t4. Улица\n\
\t5. Количество этажей\n\
\t6. Год постройки дома\n\
\t\tДоступные значения:\n\
\t\t6.1 Застройка 00-х и 10-х\n\
\t\t6.2 Новостройка\n\
\t\t6.3 Стройка\n\
\t\t6.4 Дома до 1930-х\n\
\t\t6.5 Сталинка | Хрущевка | Брежневка\n\
\t7. Тип автора\n\
\t\tДоступные значения:\n\
\t\t7.1 Агентство недвижимости\n\
\t\t7.2 Собственник\n\
\t\t7.3 Риелтор\n\
\t\t7.4 Ук оф.представитель\n\
\t\t7.5 Представитель застройщика\n\
\t\t7.6 Застройщик\n\
\t\t7.7 Без указанного типа\n\
\t8. Количество комнат\n\
\t9. Отделка\n\
\t\tДоступные значения:\n\
\t\t9.1 Неизвестно\n\
\t\t9.2 Без отделки\n\
\t\t9.3 Чистовая\n\
\t\t9.4 Предчистовая\n\
\t\t9.5 Черновая\n\
\t10. Этаж\n\
\t11. Тип дома\n\
\t\tДоступные значения:\n\
\t\t11.1 Неизвестно\n\
\t\t11.2 Монолитно-кирпичный\n\
\t\t11.3 Монолитный\n\
\t\t11.4 Панельный\n\
\t\t11.5 Кирпичный\n\n\
<u>p.s. Данные актуальны на момент марта 2024 года</u>\n\
Для старта воспользуйтесь командой /params",
parse_mode = 'html'
                    )

# Инициализируем параметры для принятия пользовательский данных и загрузки в модель
user_parameters = {
    'author_type' : '',
    'floor' : '',
    'floors_count' : '',
    'rooms_count' : '',
    'total_meters' : '',
    'year_of_construction' : '',
    'house_material_type' : '',
    'finish_type' : '',
    'living_meters' : '',
    'kitchen_meters' : '',
    'district' : '',
    'street' : '',
    'underground': '',
}

# Вот сюда сейвим пользовательский ввод
collected_params = {}

# Start сollecting params
@bot.message_handler(commands=['params'])
def start_collecting_params(message):
    markup = types.InlineKeyboardMarkup()
    itembtns = [
        types.InlineKeyboardButton('Агенство недвижимости', callback_data='real_estate_agent'),
        types.InlineKeyboardButton('Собственник', callback_data='homeowner'),
        types.InlineKeyboardButton('Риелтор', callback_data='realtor'),
        types.InlineKeyboardButton('Ук оф.представитель', callback_data='official_representative'),
        types.InlineKeyboardButton('Представитель застройщика', callback_data='representative_developer'),
        types.InlineKeyboardButton('Застройщик', callback_data='developer'),
        types.InlineKeyboardButton('Без указанного типа', callback_data='unknown')
    ]
    for item in itembtns:
        markup.add(item)

    msg = bot.send_message(message.chat.id, "<b>Выберите тип автора:</b>", reply_markup=markup, parse_mode='html')

@bot.callback_query_handler(func=lambda call: True)
def process_inline_buttons(call):
    if hasattr(call, 'data') and call.data:
        if call.data in ['real_estate_agent', 'homeowner', 'realtor', 'official_representative', 'representative_developer', 'developer', 'unknown']:
            user_parameters['author_type'] = call.data
            msg = bot.send_message(call.message.chat.id, "<b>Введите этаж (от 1 до 30):</b>", parse_mode='html')
            bot.register_next_step_handler(msg, process_floor)

        elif call.data in ['Застройка 00-х и 10-х', 'Новостройка', 'Стройка', 'Дома до 1930-х', 'Стaлинка | Хрущевка | Брежневка']:
            user_parameters['year_of_construction'] = call.data
            markup_house_material_type = types.InlineKeyboardMarkup()
            itembtns_house_material_type = [
                types.InlineKeyboardButton('Неизвестно', callback_data='Неизвестно'),
                types.InlineKeyboardButton('Монолитно-кирпичный', callback_data='Монолитно-кирпичный'),
                types.InlineKeyboardButton('Монолитный', callback_data='Монолитный'),
                types.InlineKeyboardButton('Панельный', callback_data='Панельный'),
                types.InlineKeyboardButton('Кирпичный', callback_data='Кирпичный')
            ]
            for item in itembtns_house_material_type:
                markup_house_material_type.add(item)
            msg = bot.send_message(call.message.chat.id, "<b>Введите тип дома:</b>", reply_markup=markup_house_material_type, parse_mode='html')

        elif call.data in ['Неизвестно', 'Монолитно-кирпичный', 'Монолитный', 'Панельный', 'Кирпичный'] and user_parameters['house_material_type'] == '':
            user_parameters['house_material_type'] = call.data
            markup_finish_type = types.InlineKeyboardMarkup()
            itembtns_finish_type = [
                types.InlineKeyboardButton('Неизвестно', callback_data='Неизвестно'),
                types.InlineKeyboardButton('Без отделки', callback_data='Без отделки'),
                types.InlineKeyboardButton('Чистовая', callback_data='Чистовая'),
                types.InlineKeyboardButton('Предчистовая', callback_data='Предчистовая'),
                types.InlineKeyboardButton('Черновая', callback_data='Черновая')
            ]
            for item in itembtns_finish_type:
                markup_finish_type.add(item)
            msg = bot.send_message(call.message.chat.id, "<b>Введите тип отделки:</b>", reply_markup=markup_finish_type, parse_mode='html')

        elif call.data in ['Неизвестно', 'Без отделки', 'Чистовая', 'Предчистовая', 'Черновая']:
            user_parameters['finish_type'] = call.data
            msg = bot.send_message(call.message.chat.id, "<b>Введите район Санкт-Петербурга:\nПриморский\n\
Московский\n\
Пушкинский\n\
Выборгский\n\
Невский\n\
Василеостровский\n\
Красногвардейский\n\
Петроградский\n\
Красносельский\n\
Центральный\n\
Адмиралтейский\n\
Курортный\n\
Калининский\n\
Колпинский\n\
Фрунзенский\n\
Петродворцовый\n\
Кировский</b>", parse_mode='html')
            bot.register_next_step_handler(msg, process_district)

# Process floor
def process_floor(message):
    try:
        floor = int(message.text)
        if floor < 1 or floor > 30:
            msg = bot.send_message(message.chat.id, "<b>Как-то нереалистично, пожалуйста, введите этаж (от 1 до 30):</b>", parse_mode='html')
            bot.register_next_step_handler(msg, process_floor)
        else:
            user_parameters['floor'] = floor
            msg = bot.send_message(message.chat.id, "<b>Введите этажность дома (от 1 до 30):</b>", parse_mode='html')
            bot.register_next_step_handler(msg, process_floor_count)
    except ValueError:
        msg = bot.send_message(message.chat.id, "<b>Пожалуйста, введите числовое значение (от 1 до 30):</b>", parse_mode='html')
        bot.register_next_step_handler(msg, process_floor)

# Process floor_count
def process_floor_count(message):
    try:
        floor_cnt = int(message.text)
        if floor_cnt < user_parameters['floor']:
            msg = bot.send_message(message.chat.id, "<b>Количество этажей дома не может быть меньше желаемого этажа</b>", parse_mode='html')
            bot.register_next_step_handler(msg, process_floor_count)
        elif floor_cnt < 1 or floor_cnt > 30:
            msg = bot.send_message(message.chat.id, "<b>Пожалуйста, введите этажность дома (от 1 до 30):</b>", parse_mode='html')
            bot.register_next_step_handler(msg, process_floor_count)
        else:
            user_parameters['floors_count'] = floor_cnt
            msg = bot.send_message(message.chat.id, "<b>Введите количество комнат (от 0 до 5):</b>", parse_mode='html')
            bot.register_next_step_handler(msg, process_rooms_count)
    except ValueError:
        msg = bot.send_message(message.chat.id, "<b>Пожалуйста, введите числовое значение (от 1 до 30):</b>", parse_mode='html')
        bot.register_next_step_handler(msg, process_floor_count)

# Process rooms_count
def process_rooms_count(message):
    try:
        rooms_cnt = int(message.text)
        if rooms_cnt < 0 or rooms_cnt > 5:
            msg = bot.send_message(message.chat.id, "<b>Пожалуйста, введите количество комнат в диапазоне (от 0 ло 5):</b>", parse_mode='html')
            bot.register_next_step_handler(msg, process_rooms_count)
        else:
            user_parameters['rooms_count'] = rooms_cnt
            msg = bot.send_message(message.chat.id, "<b>Введите общую площадь (от 18 до 173):</b>", parse_mode='html')
            bot.register_next_step_handler(msg, process_total_meters)
    except ValueError:
        msg = bot.send_message(message.chat.id, "<b>Пожалуйста, введите числовое значение (от 0 до 5):</b>", parse_mode='html')
        bot.register_next_step_handler(msg, process_rooms_count)

# Process total_meters including kitchen_meters and living_meters
def process_total_meters(message):
    try:
        total_meters = int(message.text)
        if total_meters < 18 or total_meters > 173:
            msg = bot.send_message(message.chat.id, "<b>Пожалуйста, введите общую  площадь в диапазоне (от 18 до 173):</b>", parse_mode='html')
            bot.register_next_step_handler(msg, process_total_meters)
        else:
            user_parameters['total_meters'] = total_meters
            markup_period_built = types.InlineKeyboardMarkup()
            itembtns_period_built = [
                types.InlineKeyboardButton('Застройка 00-х и 10-х', callback_data='Застройка 00-х и 10-х'),
                types.InlineKeyboardButton('Новостройка', callback_data='Новостройка'),
                types.InlineKeyboardButton('Стройка', callback_data='Стройка'),
                types.InlineKeyboardButton('Дома до 1930-х', callback_data='Дома до 1930-х'),
                types.InlineKeyboardButton('Стaлинка | Хрущевка | Брежневка', callback_data='Стaлинка | Хрущевка | Брежневка')
            ]

            for item in itembtns_period_built:
                markup_period_built.add(item)

            if user_parameters['rooms_count'] == 0:
                user_parameters['kitchen_meters'] = round(user_parameters['total_meters'] * 0.15, 2)
                user_parameters['living_meters'] = round(user_parameters['total_meters'] * 0.65, 2)
            elif user_parameters['rooms_count'] != 0:
                user_parameters['kitchen_meters'] = round(user_parameters['total_meters'] * 0.18, 2)
                user_parameters['living_meters'] = round(user_parameters['total_meters'] * 0.48, 2)

            msg = bot.send_message(message.chat.id, "<b>Выберите период постройки дома:</b>", reply_markup=markup_period_built, parse_mode='html')

    except ValueError:
        msg = bot.send_message(message.chat.id, "<b>Пожалуйста, введите числовое значение (от 18 до 173):</b>", parse_mode='html')
        bot.register_next_step_handler(msg, process_total_meters)

# Process district
def process_district(message):
    try:
        district = message.text.title()
        if district not in ['Приморский', 'Московский', 'Пушкинский', 'Выборгский', 'Невский',
                            'Василеостровский', 'Красногвардейский', 'Петроградский', 'Красносельский',
                            'Центральный', 'Адмиралтейский', 'Курортный', 'Калининский', 'Колпинский',
                            'Фрунзенский', 'Петродворцовый', 'Кировский']:
            msg = bot.send_message(message.chat.id, "<b>Пожалуйста, введите корректный район:</b>", parse_mode='html')
            bot.register_next_step_handler(msg, process_district)
        else:
            user_parameters['district'] = district
            if district == 'Московский':
                user_parameters['district_rating'] = 17
            elif district == 'Выборгский':
                user_parameters['district_rating'] = 16
            elif district == 'Приморский':
                user_parameters['district_rating'] = 15
            elif district == 'Калининский':
                user_parameters['district_rating'] = 14
            elif district == 'Василеостровский':
                user_parameters['district_rating'] = 13
            elif district == 'Петроградский':
                user_parameters['district_rating'] = 12
            elif district == 'Фрунзенский':
                user_parameters['district_rating'] = 11
            elif district == 'Красносельский':
                user_parameters['district_rating'] = 10
            elif district == 'Петродворцовый':
                user_parameters['district_rating'] = 9
            elif district == 'Курортный':
                user_parameters['district_rating'] = 8
            elif district == 'Невский':
                user_parameters['district_rating'] = 7
            elif district == 'Центральный':
                user_parameters['district_rating'] = 6
            elif district == 'Пушкинский':
                user_parameters['district_rating'] = 5
            elif district == 'Адмиралтейский':
                user_parameters['district_rating'] = 4
            elif district == 'Красногвардейский':
                user_parameters['district_rating'] = 3
            elif district == 'Кировский':
                user_parameters['district_rating'] = 2
            elif district == 'Колпинский':
                user_parameters['district_rating'] = 1
            msg = bot.send_message(message.chat.id, "<b>Введите улицу:</b>", parse_mode='html')
            bot.register_next_step_handler(msg, process_street)
    except ValueError:
        msg = bot.send_message(message.chat.id, "<b>Проверьте, пожалуйста, правописание</b>", parse_mode='html')
        bot.register_next_step_handler(msg, process_district)

# Process street
def process_street(message):
    street = message.text.title()
    user_parameters['street'] = street
    msg = bot.send_message(message.chat.id, "<b>Введите метро:</b>", parse_mode='html')
    bot.register_next_step_handler(msg, process_underground)

metro_stations = {
    "Приморский": ["Черная речка", "Пионерская", "Старая Деревня", "Комендантский проспект", "Беговая"],
    "Выборгский": ["Выборгская", "Лесная", "Удельная", "Озерки", "Проспект Просвещения", "Парнас"],
    "Калининский": ["Площадь Ленина", "Политехническая", "Академическая", "Гражданский проспект", "Девяткино"],
    "Красногвардейский": ["Новочеркасская", "Ладожская"],
    "Невский": ["Проспект Большевиков", "Улица Дыбенко", "Елизаровская", "Ломоносовская", "Пролетарская", "Обухово", "Рыбацкое"],
    "Центральный": ["Площадь Александра Невского", "Площадь Восстания", "Маяковская", "Лиговский проспект",
                           "Владимирская", "Достоевская", "Невский проспект", "Гостиный Двор"],
    "Василеостровский": ["Василеостровская", "Приморская", "Зенит", "Горный институт"],
    "Адмиралтейский": ["Фрунзенская", "Сенная", "Садовая", "Спасская", "Пушкинская", "Звенигородская",
                              "Технологический институт", "Балтийская", "Адмиралтейская"],
    "Петроградский": ["Петроградская", "Горьковская", "Крестовский остров", "Чкаловская", "Спортивная"],
    "Фрунзенский": ["Купчино", "Волковская", "Обводный канал",
                           "Международная", "Бухарестская", "Проспект Славы", "Дунайская"],
    "Московский": ["Московские ворота", "Электросила",
                         "Парк Победы", "Московская", "Звёздная"],
    "Кировский": ["Нарвская", "Кировский завод", "Автово",
                        "Ленинский проспект", "Проспект Ветеранов"],
    "Пушкинский" : ["Шушары"],
    "Колпинский" : ["Рыбацкое", "Звёздная"],
    "Красносельский" : ["Проспект Ветеранов"],
    "Курортный" : ["Беговая"],
    "Петродворцовый" : ["Проспект Ветеранов", "Автово"]
}

# Process underground
def process_underground(message):
    try:
        district = user_parameters['district']
        underground = message.text
        allowed_stations = metro_stations[district]

        if underground in allowed_stations:
            user_parameters['underground'] = underground
            msg = bot.send_message(message.chat.id, "<b>Параметры собраны, теперь можно предсказывать!</b>\nДля этого воспользуйтесь командой /predict", parse_mode='html')
            save_parameters()
        else:
            msg = bot.send_message(message.chat.id, f"<b>Пожалуйста, выберите станции метро для выбранного района: {', '.join(allowed_stations)}</b>", parse_mode='html')
            bot.register_next_step_handler(msg, process_underground)

    except ValueError:
        msg = bot.send_message(message.chat.id, "<b>Проверьте, пожалуйста, правописание</b>", parse_mode='html')
        bot.register_next_step_handler(msg, process_underground)

@bot.message_handler(commands=['predict'])
def prediction(message):
    try:
        user_parameters = load_user_parameters()
        input_data = pd.DataFrame(user_parameters, index=[0])
        predicted_price = np.exp(model.predict(input_data))
        lower_border = int(predicted_price - (predicted_price * 5 / 100))
        upper_border = int(predicted_price + (predicted_price * 5 / 100))
        formatted_lower_border = "{:,}".format(lower_border).replace(",", ".")
        formatted_upper_border = "{:,}".format(upper_border).replace(",", ".")
        markup = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text="Ссылка на Циан", url=generate_cian_url(user_parameters))
        markup.add(url_button)
        bot.send_message(message.chat.id, f"Предсказанная цена недвижимости: в диапазоне от <b>{formatted_lower_border}₽</b> до <b>{formatted_upper_border}₽</b>", parse_mode='html', reply_markup=markup)
    except:
        msg = bot.send_message(message.chat.id, "<b>Проверьте, пожалуйста, корректно ли вы ввели параметры</b>", parse_mode='html')
        bot.register_next_step_handler(msg, process_inline_buttons)

# Сэйвим собранные данные в json
def save_parameters():
    global user_parameters
    user_parameters.update(collected_params)

    with open('user_parameters.json', 'w', encoding='utf-8') as file:
        json.dump(user_parameters, file, ensure_ascii=False)

def load_user_parameters():
    with open('user_parameters.json', 'r', encoding='utf-8') as file:
        user_parameters = json.load(file)
    return user_parameters

subways = {
    'Беговая' : 'metro%5B0%5D=355',
    'Зенит' : 'metro%5B0%5D=356',
    'Приморская' : 'metro%5B0%5D=204',
    'Василеостровская' : 'metro%5B0%5D=205',
    'Гостиный двор' : 'metro%5B0%5D=206',
    'Маяковская' : 'metro%5B0%5D=207',
    'Площадь Александра Невского' : 'metro%5B0%5D=208',
    'Елизаровская' : 'metro%5B0%5D=210',
    'Ломоносовская' : 'metro%5B0%5D=211',
    'Пролетарская' : 'metro%5B0%5D=212',
    'Обухово' : 'metro%5B0%5D=213',
    'Рыбацкое' : 'metro%5B0%5D=214',
    'Девяткино' : 'metro%5B0%5D=167',
    'Гражданский проспект' : 'metro%5B0%5D=168',
    'Академическая' : 'metro%5B0%5D=169',
    'Политехническая' : 'metro%5B0%5D=170',
    'Площадь Мужества' : 'metro%5B0%5D=171',
    'Лесная' : 'metro%5B0%5D=172',
    'Выборгская' : 'metro%5B0%5D=173',
    'Площадь Ленина' : 'metro%5B0%5D=174',
    'Чернышевская' : 'metro%5B0%5D=175',
    'Площадь Восстания' : 'metro%5B0%5D=176',
    'Владимирская' : 'metro%5B0%5D=177',
    'Пушкинская' : 'metro%5B0%5D=178',
    'Технологический институт' : 'metro%5B0%5D=179',
    'Балтийская' : 'metro%5B0%5D=180',
    'Нарвская' : 'metro%5B0%5D=181',
    'Кировский завод' : 'metro%5B0%5D=182',
    'Автово' : 'metro%5B0%5D=183',
    'Ленинский проспект' : 'metro%5B0%5D=184',
    'Проспект Ветеранов' : 'metro%5B0%5D=185',
    'Парнас' : 'metro%5B0%5D=186',
    'Проспект Просвещения' : 'metro%5B0%5D=187',
    'Озерки' : 'metro%5B0%5D=188',
    'Удельная' : 'metro%5B0%5D=189',
    'Пионерская' : 'metro%5B0%5D=190',
    'Чёрная речка' : 'metro%5B0%5D=191',
    'Петроградская' : 'metro%5B0%5D=192',
    'Горьковская' : 'metro%5B0%5D=193',
    'Невский проспект ' : 'metro%5B0%5D=194',
    'Сенная площадь' : 'metro%5B0%5D=195',
    'Фрунзенская' : 'metro%5B0%5D=197',
    'Московские ворота' : 'metro%5B0%5D=198',
    'Электросила' : 'metro%5B0%5D=199',
    'Парк Победы' : 'metro%5B0%5D=200',
    'Московская' : 'metro%5B0%5D=201',
    'Звёздная' : 'metro%5B0%5D=202',
    'Купчино' : 'metro%5B0%5D=203',
    'Горный институт' : 'metro%5B0%5D=382',
    'Спасская' : 'metro%5B0%5D=232',
    'Достоевская' : 'metro%5B0%5D=221',
    'Лиговский проспект' : 'metro%5B0%5D=222',
    'Новочеркасская' : 'metro%5B0%5D=224',
    'Ладожская' : 'metro%5B0%5D=225',
    'Проспект Большевиков' : 'metro%5B0%5D=226',
    'Улица Дыбенко' : 'metro%5B0%5D=227',
    'Комендантский проспект' : 'metro%5B0%5D=215',
    'Старая Деревня' : 'metro%5B0%5D=216',
    'Крестовский остров' : 'metro%5B0%5D=217',
    'Чкаловская' : 'metro%5B0%5D=218',
    'Спортивная' : 'metro%5B0%5D=219',
    'Адмиралтейская' : 'metro%5B0%5D=242',
    'Садовая' : 'metro%5B0%5D=220',
    'Звенигородская' : 'metro%5B0%5D=231',
    'Обводный канал' : 'metro%5B0%5D=241',
    'Волковская' : 'metro%5B0%5D=230',
    'Бухарестская' : 'metro%5B0%5D=247',
    'Международная' : 'metro%5B0%5D=246',
    'Проспект Славы' : 'metro%5B0%5D=357',
    'Дунайская' : 'metro%5B0%5D=358',
    'Шушары' : 'metro%5B0%5D=359'
}

def generate_cian_url(user_parameters):
    base_url = 'https://spb.cian.ru/cat.php?deal_type=sale'
    total_area = f'&maxtarea={round(user_parameters["total_meters"])}'
    underground = f'&{subways[user_parameters["underground"]]}'
    floors_count = f'&maxfloorn={user_parameters["floors_count"]}'
    if user_parameters['rooms_count'] > 0:
        rooms_count = f'&room{user_parameters["rooms_count"]}=1'
    else:
        rooms_count = f'&room9=1'
    floor = f'&maxfloor={user_parameters["floor"]}'


    return f'{base_url}{total_area}{underground}{floors_count}{floor}{rooms_count}'

# Пока не понимаю как работает но с кнопками вроде норм
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    bot.send_message(message.chat.id, "<b>Пожалуйста, выберите с помощью кнопок или команд</b>", parse_mode='html')

## Обработать exit, для след.параметров логика такая же, вроде все работает
bot.infinity_polling()

"""
def main():
    start_message(message)
    bot.infinity_poling()

if __name__ == '__main__':
    main()
"""
