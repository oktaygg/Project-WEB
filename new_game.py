from telegram.ext import Application
from telegram.ext import MessageHandler
from telegram.ext import filters
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
import requests
import sys
import random
import logging

with open('goroda.txt', encoding='utf-8') as txt:
    TOWNS = txt.readlines()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

reply_keyboard = [['🎮 play 🎮', '⚙️ settings ⚙️'], ['📊 statistics 📊', '📖 faq 📖']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False)


async def start(update, context):
    await update.message.reply_text(
        "Я бот-игра! Используйте команды для старта игры!",
        reply_markup=markup
    )
    return context


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Клавиатура закрыта. Испоьзуйте /start для её запуска!",
        reply_markup=ReplyKeyboardRemove())
    return context


async def helpp(update, context):
    await update.message.reply_text("Я бот, команда в разработке.")
    return context


async def stat(update, context):
    await update.message.reply_text("В разработке.")
    return context


async def search(towngg):
    geocoder_request = (f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0"
                        f"493-4b70-98ba-98533de7710b&geocode={towngg}&format=json")
    response = requests.get(geocoder_request)
    if not response:
        print("Ошибка выполнения запроса:")
        return [1000 - 7]
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    return ','.join(toponym_coodrinates.split(' '))


async def play(update, context):
    town = random.choice(TOWNS)[:-1]
    cords = await search(town)
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={cords}&spn=0.05,0.05&l=sat"
    response = requests.get(map_request)
    if not response:
        print("Ошибка выполнения запроса:")
        sys.exit(1)
    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    await update.message.reply_text(
        "Привет. Угадайте город по фото:")
    await update.message.reply_photo('map.png')
    await update.message.reply_text(
        "Введите название города:")
    context.user_data['locality'] = [town, cords]
    context.user_data['isgame'] = 'wait town'


async def first_response(update, context):
    context.user_data['locality'] = context.user_data['locality'] + [update.message.text]
    s = context.user_data['locality']
    try:
        cords2 = await search(context.user_data['locality'][2])
    except Exception as error:
        logging.exception(error)
        cords2 = '123'
    await update.message.reply_text(f'Вы угадали город - {s[0]}\nоцените игру от 1 до 5' if cords2 == s[
        1] else f'Вы не угадали город {s[0]}, выбрав - {s[2]}\nоцените игру от 1 до 5')
    context.user_data['isgame'] = 'wait number'


async def second_response(update, context):
    await update.message.reply_text(f"Спасибо за участие! Статистика в разработке!")
    del context.user_data['isgame']
    del context.user_data['locality']


async def check_command(update, context):
    if 'isgame' in context.user_data:
        if context.user_data['isgame'] == 'wait town':
            await first_response(update, context)
        elif context.user_data['isgame'] == 'wait number':
            await second_response(update, context)
    elif update.message.text == '🎮 play 🎮':
        await play(update, context)
    elif update.message.text == '📊 statistics 📊':
        await stat(update, context)
    elif update.message.text == '📖 faq 📖':
        await helpp(update, context)
    elif update.message.text == '🚪 exit 🚪':
        await close_keyboard(update, context)
    elif update.message.text == '⚙️ settings ⚙️':
        await first_key_buttons(update, context)


async def button(update, context):
    query = update.callback_query

    await query.answer()

    answer = str(query.data)

    if answer == "стата":
        await query.edit_message_text(text="vot tebe stata")
    elif answer == "далее":
        await second_key_buttons(update, context, 2)
    elif answer == 'назад':
        await second_key_buttons(update, context, 1)
    return context


async def first_key_buttons(update, context):
    keyboard = [
        [
            InlineKeyboardButton("стата", callback_data='стата'),
            InlineKeyboardButton("далее", callback_data='далее'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("1", reply_markup=reply_markup)
    return context


async def second_key_buttons(update, context, count):
    query = update.callback_query
    if count == 1:
        keyboard = [
            [
                InlineKeyboardButton("стата", callback_data='стата'),
                InlineKeyboardButton("далее", callback_data='далее'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="1s", reply_markup=reply_markup)
    elif count == 2:
        keyboard = [
            [
                InlineKeyboardButton("помощь", callback_data="помощь"),
                InlineKeyboardButton("назад", callback_data='назад'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="2", reply_markup=reply_markup)
    return context


def main():
    application = Application.builder().token('7198751024:AAF8hG5IUJq-BNMJ6BQ0FtH6kQgUDdT7C7I').build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_command))

    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()


if __name__ == '__main__':
    main()