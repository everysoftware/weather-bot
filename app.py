import json
import asyncio

import telebot.async_telebot
import requests

import config
import sql
import subscription

WELCOME_STR = 'Привет, я бот, сообщающий текущую погоду! Чтобы узнать погоду в городе, укажи'
WEATHER_STR = 'Напечатай название своего города.'
INFO_STR = "<b>Погода ({})</b>\n\n" + \
           "Температура: {}°C {}\n" + \
           "Ощущается как: {}°C {}\n" + \
           "Давление: {} гПа\n" + \
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
        kb = [
            telebot.types.KeyboardButton('Отправить геолокацию 📍', request_location=True),
            telebot.types.KeyboardButton('Погода в городе ⛅️'),
            telebot.types.KeyboardButton('Оформить подписку ⭐️'),
        ]
        markup = telebot.types.ReplyKeyboardMarkup(
            row_width=2,
            one_time_keyboard=True,
            resize_keyboard=True
        )
        markup.add(*kb)
        await bot.send_message(msg.chat.id, WELCOME_STR, reply_markup=markup)


@bot.message_handler(content_types=['location'])
async def location_callback(msg):
    await bot.reply_to(msg,
                       get_weather(longitude=msg.location.longitude, latitude=msg.location.latitude),
                       parse_mode='html')


@bot.message_handler(text=['Погода в городе ⛅️', 'Оформить подписку ⭐️'])
async def menu_callback(msg):
    if msg.text == 'Погода в городе ⛅️':
        await weather_handler(msg)
    elif msg.text == 'Оформить подписку ⭐️':
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


def parse_json(response):
    data = json.loads(response.text)
    return INFO_STR.format(data['name'],
                           data['main']['temp'], get_temp_emoji(data['main']['temp']),
                           data['main']['feels_like'], get_temp_emoji(data['main']['feels_like']),
                           data['main']['pressure'],
                           data['main']['humidity']
                           )


@bot.message_handler(commands=['author'])
async def author_handler(msg):
    await bot.send_message(msg.chat.id, 'Автор бота: @ivanstasevich')


def get_weather(city=None, longitude=None, latitude=None):
    if city is not None:
        response = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={config.OPEN_WEATHER_KEY}'
            f'&units=metric')
    elif longitude is not None and latitude is not None:
        response = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&'
            f'APPID={config.OPEN_WEATHER_KEY}&units=metric')
    else:
        raise ValueError
    text = parse_json(response) if response.ok else NOT_FOUND_STR
    return text


@bot.message_handler()
async def get_weather_handler(msg):
    city = msg.text.strip().lower()
    await bot.reply_to(msg, get_weather(city), parse_mode='html')


def main():
    from subscription import bot
    print('Polling...')
    asyncio.run(bot.infinity_polling())


if __name__ == '__main__':
    main()
