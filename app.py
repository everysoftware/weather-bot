import json
import asyncio

import telebot.async_telebot
import requests

import config
import sql
import subscription


WELCOME_STR = 'Привет, я бот, сообщающий текущую погоду!'
WEATHER_STR = 'Напечатай название своего города.'
INFO_STR = "<b>Погода ({})</b>\n\n" +\
           "Температура: {}°C {}\n" +\
           "Ощущается как: {}°C {}\n" +\
           "Давление: {} гПа\n" +\
           "Влажность: {}%\n"
NOT_FOUND_STR = 'Город не найден!'
UNKNOWN_COMMAND_STR = 'Неизвестная команда.'

db = sql.Database('bot.db')
bot = telebot.async_telebot.AsyncTeleBot(config.TG_TOKEN, parse_mode='HTML')


@bot.message_handler(commands=['start'])
async def start_handler(msg):
    try:
        await db.add_user(msg.chat.id, msg.chat.first_name)
    except ValueError:
        pass
    finally:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(telebot.types.KeyboardButton('Узнать погоду'))
        markup.add(telebot.types.KeyboardButton('Оформить подписку'))
        await bot.send_message(msg.chat.id, WELCOME_STR, reply_markup=markup)


@bot.message_handler(text=['Узнать погоду', 'Оформить подписку'])
async def menu_callback(msg):
    if msg.text == 'Узнать погоду':
        await weather_handler(msg)
    elif msg.text == 'Оформить подписку':
        await subscription.main_handler(msg)


@bot.message_handler(commands=['weather'])
async def weather_handler(msg):
    await bot.reply_to(msg, WEATHER_STR)

bot.add_custom_filter(telebot.asyncio_filters.TextMatchFilter())


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


@bot.message_handler(commands=['author'])
async def author_handler(msg):
    await bot.send_message(msg.chat.id, 'Автор бота: @ivanstasevich')


@bot.message_handler()
async def get_weather(msg):
    city = msg.text.strip().lower()
    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={config.OPEN_WEATHER_KEY}'
                            f'&units=metric')
    text = parse_json(city, response) if response.ok else NOT_FOUND_STR
    await bot.reply_to(msg, text, parse_mode='html')


def main():
    from subscription import bot
    print('Polling...')
    asyncio.run(bot.infinity_polling())


if __name__ == '__main__':
    main()
