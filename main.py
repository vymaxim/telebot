import threading
import time
import datetime

import schedule

import telebot as tb
from telebot import types

from models import Post
from views import add_into_db, create_connection, get_plants_id_name, get_choice, get_plants_info, update_time, \
    change_info_in_database, delete_plant_in_database


bot = tb.TeleBot('1883674015:AAFiquNVBWcx7Lsm1MItI9pzwHitmy2W2oE')
create_connection()

users_list_id = (982431322, 326179308)


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == "/start":
        if message.from_user.id not in users_list_id:
            bot.send_message(message.chat.id, 'С вами разговаривать я не буду!')
        else:
            global chat_id, main_menu
            chat_id = message.chat.id
            main_menu = types.InlineKeyboardMarkup(row_width=2)
            add_new_plants = types.InlineKeyboardButton(text='Добавить новое растение', callback_data='add_new_plants')
            get_plant_description = types.InlineKeyboardButton(text='Выберите растения', callback_data='get_plant_menu')
            main_menu.add(add_new_plants, get_plant_description)
            question = 'Выбери что интересует'
            bot.send_message(message.from_user.id, text=question, reply_markup=main_menu)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "main_menu":
        main_menu = types.InlineKeyboardMarkup(row_width=2)
        add_new_plants = types.InlineKeyboardButton(text='Добавить новое растение',
                                                    callback_data='add_new_plants')
        get_plant_description = types.InlineKeyboardButton(text='Выберите растения', callback_data='get_plant_menu')
        main_menu.add(add_new_plants, get_plant_description)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=main_menu)

    if call.data == 'get_plant_menu':
        get_plant_menu = types.InlineKeyboardMarkup(row_width=2)
        plants = get_plants_id_name()
        get_plant_menu.add(types.InlineKeyboardButton(text=f'назад', callback_data=f'main_menu'))
        for id, name in plants:
            get_plant_menu.add(types.InlineKeyboardButton(text=f'{name}', callback_data=f'choice_menu={id}'))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_plant_menu)

    if 'choice_menu=' in call.data:
        id = call.data.split('=')[1]
        choice_menu = types.InlineKeyboardMarkup()
        choice_menu.add(types.InlineKeyboardButton(text=f'назад', callback_data=f'get_plant_menu'))
        choice_menu.add(types.InlineKeyboardButton(text=f'Внести изменения', callback_data=f'change_info={id}'))
        choice_menu.add(types.InlineKeyboardButton(text=f'Описание', callback_data=f'choice=description={id}'))
        choice_menu.add(types.InlineKeyboardButton(text=f'Дата следующего полива', callback_data=f'choice=next_watering_at={id}'))
        choice_menu.add(types.InlineKeyboardButton(text=f'Дата следующего удобрения', callback_data=f'choice=next_fertilization_at={id}'))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=choice_menu)

    if 'choice=' in call.data:
        choice = get_choice(call.data.split('=')[1], call.data.split('=')[2])
        bot.send_message(call.message.chat.id, choice)

    if 'change_info=' in call.data:
        id = call.data.split('=')[1]
        change_info_menu = types.InlineKeyboardMarkup()
        change_info_menu.add(types.InlineKeyboardButton(text=f'назад', callback_data=f'choice_menu={id}'))
        change_info_menu.add(types.InlineKeyboardButton(text=f'Название', callback_data=f'change_info_func=name={id}'))
        change_info_menu.add(types.InlineKeyboardButton(text=f'Описание', callback_data=f'change_info_func=description={id}'))
        change_info_menu.add(types.InlineKeyboardButton(text=f'Период полива', callback_data=f'change_info_func=watering_period={id}'))
        change_info_menu.add(types.InlineKeyboardButton(text=f'Период удобрения', callback_data=f'change_info_func=fertilization_period={id}'))
        change_info_menu.add(types.InlineKeyboardButton(text=f'Удалить', callback_data=f'change_info_func=delete={id}'))

        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=change_info_menu)

    if 'change_info_func=' in call.data:
        global lst
        lst = call.data.split('=')[1:]
        if 'delete' in call.data:
            bot.send_message(call.from_user.id, 'Подтвердите удаление, написав "Да"')
            bot.register_next_step_handler(call.message, change_info)
        elif 'name' in call.data:
            bot.send_message(call.from_user.id, 'Измените название растения')
            bot.register_next_step_handler(call.message, change_info)
        elif 'description' in call.data:
            bot.send_message(call.from_user.id, 'Измените описание растения')
            bot.register_next_step_handler(call.message, change_info)
        elif 'watering_period' in call.data:
            bot.send_message(call.from_user.id, 'Измените период полива растения')
            bot.register_next_step_handler(call.message, change_info)
        elif 'fertilization_period' in call.data:
            bot.send_message(call.from_user.id, 'Измените период удобрения растения')
            bot.register_next_step_handler(call.message, change_info)

    if call.data == 'add_new_plants':
        global plant
        plant = Post()
        get_new_plant(call.message)


@bot.message_handler(content_types=['text'])
def get_new_plant(message):
    bot.send_message(message.chat.id, 'Введите название растения')
    bot.register_next_step_handler(message, get_new_name)


def get_new_name(message):
    plant.name = message.text
    bot.send_message(message.chat.id, 'Введите описание растения')
    bot.register_next_step_handler(message, get_new_description)


def get_new_description(message):
    plant.description = message.text
    bot.send_message(message.chat.id, 'Введите прошлую дату полива в формате дд.мм.гггг')
    bot.register_next_step_handler(message, get_new_watering_at)


def get_new_watering_at(message):
    if validate_date(message.text):
        plant.watering_at = datetime.datetime.strptime(message.text, '%d.%m.%Y')
        bot.send_message(message.chat.id, 'Введите период с которым поливаете растение')
        bot.register_next_step_handler(message, get_new_watering_period)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Введите дату в формате дд.мм.гггг')
        bot.register_next_step_handler(message, get_new_watering_at)


def get_new_watering_period(message):
    if validate_int(message.text):
        plant.watering_period = int(message.text)
        bot.send_message(message.chat.id, 'Введите время последнего удобрения в формате дд.мм.гггг')
        bot.register_next_step_handler(message, get_new_fertilization_at)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Введите число')
        bot.register_next_step_handler(message, get_new_watering_period)


def get_new_fertilization_at(message):
    if validate_date(message.text):
        plant.fertilization_at = datetime.datetime.strptime(message.text, '%d.%m.%Y')
        bot.send_message(message.chat.id, 'Введите период с которым вы удобряете растение')
        bot.register_next_step_handler(message, get_new_fertilization_period)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Введите дату в формате дд.мм.гггг')
        bot.register_next_step_handler(message, get_new_fertilization_at)


def get_new_fertilization_period(message):
    if validate_int(message.text):
        plant.fertilization_period = int(message.text)
        add_new_plant(message)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Введите число')
        bot.register_next_step_handler(message, get_new_fertilization_period)


def change_info(message):
    if message.text.lower() == 'да':
        delete_plant_in_database(lst[1])
        bot.send_message(message.chat.id, 'Растение удалено')
    else:
        if 'period' in lst[0]:
            if validate_int(message.text):
                change_info_in_database(lst[0], lst[1], message.text)
                bot.send_message(message.chat.id, 'Изменения внесены')
            else:
                bot.send_message(message.chat.id, 'Ошибка. Введите число')
                bot.register_next_step_handler(message, change_info)
        else:
            if lst[0] == 'name':
                bot.send_message(message.chat.id, 'Название обновлено')
            elif lst[0] == 'description':
                bot.send_message(message.chat.id, 'Описание обновлено')


def validate_int(text):
    try:
        if not text.isdigit():
            raise ValueError
        else:
            return True
    except ValueError:
        print('Ошибка ввода. Введено не число')


def validate_date(text):
    try:
        if text != datetime.datetime.strptime(text, '%d.%m.%Y').strftime('%d.%m.%Y'):
            raise ValueError
        else:
            return True
    except ValueError:
        print('Ошибка ввода. Введена дата не в формате дд.мм.гггг')
        return False


def add_new_plant(message):
    add_into_db(plant)
    bot.send_message(message.chat.id, 'Растение добавлено')


def check_time():
    current_day = datetime.date.today()
    plants_info = get_plants_info()
    for id, name, next_watering_at, next_fertilization_at in plants_info:
        if next_watering_at == current_day:
            [(lambda user: bot.send_message(user, f'Пора поливать растение {name}'))(user) for user in users_list_id]
            update_time(id=id, watering=True)
        if next_fertilization_at == current_day:
            [(lambda user: bot.send_message(user, f'Пора поливать растение {name}'))(user) for user in users_list_id]
            update_time(id=id, fertilization=True)


def bot_start():
    bot.polling(none_stop=True, interval=0)


def sda():
    while True:
        schedule.run_pending()
        time.sleep(1)


# schedule.every(5).seconds.do(check_time)
schedule.every().day.at("12:00").do(check_time)

t1 = threading.Thread(target=sda)
t2 = threading.Thread(target=bot_start)
t1.start()
t2.start()
t1.join()
t2.join()