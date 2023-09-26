import string
import random

import telebot
from yoomoney import Quickpay, Client

import config
from app import bot, db


@bot.message_handler(commands=['subscribe'])
async def main_handler(msg):
    data = await db.get_payment_status(msg.chat.id)
    bought, label = data[0][0], data[0][1]

    if bought:
        await bot.reply_to(msg, 'У вас уже оформлена подписка. Приятного пользования :)')
    else:
        await p2p_buy(msg)


async def p2p_buy(msg):
    alphabet = string.ascii_lowercase + string.digits
    rand_string = ''.join(random.sample(alphabet, 10))
    quick_pay = Quickpay(
        receiver=config.YOOMONEY_RECEIVER,
        quickpay_form='shop',
        targets='Test',
        paymentType='SB',
        sum=0,
        label=rand_string
    )

    await db.update_label(rand_string, msg.chat.id)

    claim_kb = [
        [telebot.types.InlineKeyboardButton(text='Перейти к оплате',
                                            url=quick_pay.redirected_url)],
        [telebot.types.InlineKeyboardButton(text='Проверить оплату',
                                            callback_data='btn:claim')]
    ]
    claim = telebot.types.InlineKeyboardMarkup(keyboard=claim_kb)

    await bot.reply_to(msg, '<b>Оформление подписки</b>\n\nСтоимость подписки: 100 руб.\nНажмите на кнопку "Перейти к '
                            'оплате", после успешной оплаты нажмите "Проверить оплату" 🤑',
                       reply_markup=claim)


@bot.callback_query_handler(func=lambda callback: True)
async def check_payment(call):
    if call.data == 'btn:claim':
        data = await db.get_payment_status(call.message.chat.id)
        bought, label = data[0][0], data[0][1]

        if not bought:
            client = Client(config.YOOMONEY_TOKEN)
            history = client.operation_history(label=label)
            if history.operations:
                op = history.operations[-1]
                if op.status == 'success':
                    await db.update_payment_status(call.message.chat.id)
                    await bot.reply_to(call.message, 'Подписка успешно оформлена!')
                else:
                    await bot.reply_to(call.message, 'Оплата не удалась.')
            else:
                await bot.reply_to(call.message, 'Оплата не была произведена либо ещё в обработке.')
        else:
            await bot.reply_to(call.message, 'У вас уже оформлена подписка. Приятного пользования :)')

        await bot.answer_callback_query(call.id)
