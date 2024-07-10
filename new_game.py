from telegram.ext import Application
from telegram.ext import MessageHandler
from telegram.ext import filters
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
import random
import logging

TOWNS = ['Moscow', 'Saint Peterburg', 'Kazan']
PHOTOS = {'Moscow': ['Moscow_1.jpg'], 'Saint Peterburg': ['Saint_peterburg_1.jpg'], 'Kazan': ['Kazan_1.jpg']}
NAME_TOWNS = {'Moscow': ["Москва", 'москва'],
              'Saint Peterburg': ['Санкт-Петербург', "спб", "Спб", "СПБ", "питер", "Питер", "санкт петербург",
                                  "Санкт петербург", "Санкт Петербург", "санкт-петербург", "Санкт-петербург"],
              'Kazan': ["Казань", "казань"]}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

reply_keyboard = [['🎮 играть 🎮', '⚙️ настройки ⚙️'], ['📊 статистика 📊', '📖 информация 📖']]
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


async def info(update, context):
    await update.message.reply_text("Я бот, команда в разработке.")
    return context


async def stat(update, context):
    await update.message.reply_text("В разработке.")
    return context


async def play(update, context):
    town = random.choice(TOWNS)
    photo = random.choice(PHOTOS[town])
    await update.message.reply_text("Здравствуйте. Угадайте город по фото:")
    await update.message.reply_photo(rf'Russia cities\{town}\{photo}')
    await update.message.reply_text("Введите название города:")
    context.user_data['locality'] = [NAME_TOWNS[town]]
    context.user_data['isgame'] = 'wait town'


async def first_response(update, context):
    context.user_data['locality'] = context.user_data['locality'] + [update.message.text]
    s = context.user_data['locality']
    await update.message.reply_text(f'Вы угадали город - {s[0][0]}\nоцените игру от 1 до 5' if s[1] in s[
        0] else f'Вы не угадали город {s[0][0]}, выбрав - {s[1]}\nоцените игру от 1 до 5')
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
    elif update.message.text == '🎮 играть 🎮':
        await play(update, context)
    elif update.message.text == '📊 статистика 📊':
        await stat(update, context)
    elif update.message.text == '📖 информация 📖':
        await info(update, context)
    elif update.message.text == '🚪 выход 🚪':
        await close_keyboard(update, context)
    elif update.message.text == '⚙️ настройки ⚙️':
        await settings(update, context)


async def button(update, context):
    query = update.callback_query
    await query.answer()
    answer = str(query.data)

    if answer == "сложность":
        await second_settings(update, context, "сложность")
    elif answer == "профиль":
        await query.edit_message_text(text="В разработке")
    elif answer == "закрыть":
        await query.edit_message_text(text="Настройки закрыты")
    elif answer in ["лёгкая", "средняя", "сложная", "смешанная"]:
        await query.edit_message_text(text=f"Ваша сложность изменена на {answer}")
    elif answer == 'назад':
        await second_settings(update, context, 'назад')
    return context


async def settings(update, context):
    keyboard = [
        [
            InlineKeyboardButton("сложность", callback_data='сложность'),
            InlineKeyboardButton("профиль", callback_data='профиль'),
            InlineKeyboardButton("закрыть", callback_data='закрыть')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚙️               Настройки               ⚙️", reply_markup=reply_markup)
    return context


async def second_settings(update, context, count):
    query = update.callback_query
    if count == "сложность":
        keyboard = [
            [
                InlineKeyboardButton("легкая", callback_data='лёгкая'),
                InlineKeyboardButton("средняя", callback_data='средняя'),
                InlineKeyboardButton("сложная", callback_data='сложная')],
            [
                InlineKeyboardButton("смешанная", callback_data='смешанная'),
                InlineKeyboardButton("назад", callback_data='назад'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="⚙️ Выберите сложность ⚙️", reply_markup=reply_markup)
    elif count == "назад":
        keyboard = [
            [
                InlineKeyboardButton("сложность", callback_data='сложность'),
                InlineKeyboardButton("профиль", callback_data='профиль'),
                InlineKeyboardButton("закрыть", callback_data='закрыть')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("⚙️               Настройки               ⚙️", reply_markup=reply_markup)
    return context


def main():
    application = Application.builder().token('7198751024:AAF8hG5IUJq-BNMJ6BQ0FtH6kQgUDdT7C7I').build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_command))

    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()


if __name__ == '__main__':
    main()
