import json

import telebot
import requests

TG_TOKEN = 'TG_TOKEN'
OPEN_WEATHER_KEY = 'OPEN_WEATHER_TOKEN'

WELCOME_STR = 'Привет, я бот, сообщающий текущую погоду!'
WEATHER_STR = 'Напечатай название своего города.'
INFO_STR = "<b>Погода ({})</b>\n\n" +\
           "Температура: {}°C {}\n" +\
           "Ощущается как: {}°C {}\n" +\
           "Давление: {} мм. рт. ст.\n" +\
           "Влажность: {}%\n"
NOT_FOUND_STR = 'Город не найден!'
UNKNOWN_COMMAND_STR = 'Неизвестная команда.'

bot = telebot.TeleBot(TG_TOKEN)


@bot.message_handler(commands=['start'])
def start_handler(msg):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add(telebot.types.KeyboardButton('Узнать погоду'))
    bot.send_message(msg.chat.id, WELCOME_STR, reply_markup=markup)
    bot.register_next_step_handler(msg, menu_callback)


def menu_callback(msg):
    if msg.text == 'Узнать погоду':
        weather_handler(msg)
    else:
        bot.send_message(msg.chat.id, UNKNOWN_COMMAND_STR)


@bot.message_handler(commands=['weather'])
def weather_handler(msg):
    bot.reply_to(msg, WEATHER_STR)
    bot.register_next_step_handler(msg, get_weather)


def get_temp_emoji(temp):
    if temp >= 30:
        return '🔥'
    elif 10 <= temp < 30:
        return '☀️'
    elif -10 <= temp < 10:
        return '🌬'
    elif temp < -10:
        return '❄️'


def parse_json(city, response):
    data = json.loads(response.text)
    return INFO_STR.format(city.capitalize(),
                           data['main']['temp'], get_temp_emoji(data['main']['temp']),
                           data['main']['feels_like'], get_temp_emoji(data['main']['feels_like']),
                           data['main']['pressure'],
                           data['main']['humidity']
                           )


def get_weather(msg):
    city = msg.text.strip().lower()
    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={OPEN_WEATHER_KEY}&units'
                            f'=metric')
    text = parse_json(city, response) if response.ok else NOT_FOUND_STR
    bot.reply_to(msg, text, parse_mode='html')


@bot.message_handler(commands=['author'])
def author_handler(msg):
    bot.send_message(msg.chat.id, 'Автор бота: @ivanstasevich')


def main():
    bot.infinity_polling()


if __name__ == '__main__':
    main()
