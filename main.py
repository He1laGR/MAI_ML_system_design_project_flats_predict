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
\t4. Площадь кухни\n\
\t5. Улица\n\
\t6. Количество этажей\n\
\t7. Площадь жилого помещения\n\
\t8. Год постройки дома\n\
\t\tДоступные значения:\n\
\t\t8.1 Застройка 00-х и 10-х\n\
\t\t8.2 Новостройка\n\
\t\t8.3 Стройка\n\
\t\t8.4 Дома до 1930-х\n\
\t\t8.5 Сталинка | Хрущевка | Брежневка\n\
\t9. Тип автора\n\
\t\tДоступные значения:\n\
\t\t9.1 real_estate_agent - агентство недвижимости\n\
\t\t9.2 homeowner - собственник\n\
\t\t9.3 realtor - риелтор\n\
\t\t9.4 official_representative - ук оф.представитель\n\
\t\t9.5 representative_developer - представитель застройщика\n\
\t\t9.6 developer - застройщик\n\
\t\t9.7 unknown - без указанного типа\n\
\t10. Количество комнат\n\
\t11. Отделка\n\
\t\tДоступные значения:\n\
\t\t11.1 Неизвестно\n\
\t\t11.2 Без отделки\n\
\t\t11.3 Чистовая\n\
\t\t11.4 Предчистовая\n\
\t\t11.5 Черновая\n\
\t12. Этаж\n\
\t13. Тип дома\n\
\t\tДоступные значения:\n\
\t\t13.1 Неизвестно\n\
\t\t13.2 Монолитно-кирпичный\n\
\t\t13.3 Монолитный\n\
\t\t13.4 Панельный\n\
\t\t13.5 Кирпичный\n\n\
<u> p.s. Данные актуальны на момент марта 2024 года</u>\n\
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

    msg = bot.send_message(message.chat.id, "Выберите тип автора:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def process_inline_buttons(call):
    if hasattr(call, 'data') and call.data:
        if call.data in ['real_estate_agent', 'homeowner', 'realtor', 'official_representative', 'representative_developer', 'developer', 'unknown']:
            user_parameters['author_type'] = call.data
            msg = bot.send_message(call.message.chat.id, "Введите этаж (от 1 до 30):")
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
            msg = bot.send_message(call.message.chat.id, "Введите тип дома:", reply_markup=markup_house_material_type)

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
            msg = bot.send_message(call.message.chat.id, "Введите тип отделки:", reply_markup=markup_finish_type)

        elif call.data in ['Неизвестно', 'Без отделки', 'Чистовая', 'Предчистовая', 'Черновая']:
            user_parameters['finish_type'] = call.data
            msg = bot.send_message(call.message.chat.id, "Введите район Санкт-Петербурга:\nПриморский\n\
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
Кировский")
            bot.register_next_step_handler(msg, process_district)

# Process floor
def process_floor(message):
    try:
        floor = int(message.text)
        if floor < 1 or floor > 30:
            msg = bot.send_message(message.chat.id, "Как-то нереалистично, пожалуйста, введите этаж (от 1 до 30):")
            bot.register_next_step_handler(msg, process_floor)
        else:
            user_parameters['floor'] = floor
            msg = bot.send_message(message.chat.id, "Введите этажность дома (от 1 до 30):")
            bot.register_next_step_handler(msg, process_floor_count)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите числовое значение (от 1 до 30):")
        bot.register_next_step_handler(msg, process_floor)

# Process floor_count
def process_floor_count(message):
    try:
        floor_cnt = int(message.text)
        if floor_cnt < user_parameters['floor']:
            msg = bot.send_message(message.chat.id, "Количество этажей не может быть меньше желаемого этажа")
            bot.register_next_step_handler(msg, process_floor_count)
        elif floor_cnt < 1 or floor_cnt > 30:
            msg = bot.send_message(message.chat.id, "Здесь тоже, пожалуйста, введите этажность дома (от 1 до 30):")
            bot.register_next_step_handler(msg, process_floor_count)
        else:
            user_parameters['floors_count'] = floor_cnt
            msg = bot.send_message(message.chat.id, "Введите количество комнат (от 0 до 5):")
            bot.register_next_step_handler(msg, process_rooms_count)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите числовое значение (от 1 до 30):")
        bot.register_next_step_handler(msg, process_floor_count)

# Process rooms_count
def process_rooms_count(message):
    try:
        rooms_cnt = int(message.text)
        if rooms_cnt < 0 or rooms_cnt > 5:
            msg = bot.send_message(message.chat.id, "Пожалуйста, введите количество комнат в диапазоне (от 0 ло 5):")
            bot.register_next_step_handler(msg, process_rooms_count)
        else:
            user_parameters['rooms_count'] = rooms_cnt
            msg = bot.send_message(message.chat.id, "Введите общую площадь (от 18 до 173):")
            bot.register_next_step_handler(msg, process_total_meters)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите числовое значение (от 0 до 5):")
        bot.register_next_step_handler(msg, process_rooms_count)

# Process total_meters including kitchen_meters and living_meters
def process_total_meters(message):
    try:
        total_meters = int(message.text)
        if total_meters < 18 or total_meters > 173:
            msg = bot.send_message(message.chat.id, "Пожалуйста, введите общую  площадь в диапазоне (от 18 до 173):")
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

            msg = bot.send_message(message.chat.id, "Выберите период постройки дома:", reply_markup=markup_period_built)

    except ValueError:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите числовое значение (от 18 до 173):")
        bot.register_next_step_handler(msg, process_total_meters)

# Process district
def process_district(message):
    try:
        district = message.text.title()
        if district not in ['Приморский', 'Московский', 'Пушкинский', 'Выборгский', 'Невский',
                            'Василеостровский', 'Красногвардейский', 'Петроградский', 'Красносельский',
                            'Центральный', 'Адмиралтейский', 'Курортный', 'Калининский', 'Колпинский',
                            'Фрунзенский', 'Петродворцовый', 'Кировский']:
            msg = bot.send_message(message.chat.id, "Пожалуйста, введите корректный район:")
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
            msg = bot.send_message(message.chat.id, "Введите улицу:")
            bot.register_next_step_handler(msg, process_street)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Проверьте, пожалуйста, правописание")
        bot.register_next_step_handler(msg, process_district)

# Process street
def process_street(message):
    street = message.text.title()
    user_parameters['street'] = street
    msg = bot.send_message(message.chat.id, "Введите метро:")
    bot.register_next_step_handler(msg, process_underground)

metro_stations = {
    "Приморский": ["Черная речка", "Пионерская", "Старая Деревня", "Комендантский проспект", "Беговая"],
    "Выборгский": ["Выборгская", "Лесная", "Удельная", "Озерки", "Проспект Просвещения", "Парнас"],
    "Калининский": ["Площадь Ленина", "Политехническая", "Академическая", "Гражданский проспект"],
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
            msg = bot.send_message(message.chat.id, "Параметры собраны, теперь можно предсказывать!\n Для этого воспользуйтесь /predict")
            save_parameters()
        else:
            msg = bot.send_message(message.chat.id, f"Пожалуйста, выберите станции метро для выбранного района: {', '.join(allowed_stations)}")
            bot.register_next_step_handler(msg, process_underground)

    except ValueError:
        msg = bot.send_message(message.chat.id, "Проверьте, пожалуйста, правописание")
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
        bot.send_message(message.chat.id, f"Предсказанная цена недвижимости: в диапазоне от {formatted_lower_border}₽ до {formatted_upper_border}₽")
    except:
        msg = bot.send_message(message.chat.id, "Проверьте, пожалуйста, корректно ли вы ввели параметры")
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
'''
Функция на доработку, передавать фильтры пользователя и выводить страничку в циан
def generate_cian_url(user_parameters):
    # Здесь генерируйте URL для поиска на сайте ЦИАН с учетом параметров пользователя
    return "https://www.cian.ru/search/?parameters=your_parameters_here"'''

# Пока не понимаю как работает но с кнопками вроде норм
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    bot.send_message(message.chat.id, "Пожалуйста, выберите с помощью кнопок или команд")

## Обработать exit, для след.параметров логика такая же, вроде все работает
bot.infinity_polling()

"""
def main():
    start_message(message)
    bot.infinity_poling()

if __name__ == '__main__':
    main()
"""
