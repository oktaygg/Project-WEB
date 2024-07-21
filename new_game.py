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

# DATA = {user_id: [hard, points]}
DATA = {}
with open('data.txt', encoding='utf-8') as DATA_READ:
    DATA_READ = DATA_READ.readlines()
    for el in DATA_READ:
        el = el.split('/')
        DATA[el[0]] = [el[1], el[2][:-1]]

RUWORDS = {'easy': 'лёгкая', 'medium': 'средняя', 'hard': 'сложная', 'multy': 'смешанная'}
ENWORDS = {'лёгкая': 'easy', 'средняя': 'medium', 'сложная': 'hard', 'смешанная': 'multy'}

TOWNS = {'easy': ['Moscow', 'Saint Peterburg', 'Sochi'], 'medium': ['Kazan', 'Ekaterenburg'], 'hard': ['Arhangelsk']}

PHOTOS = {'Moscow': ['Moscow_1.jpg', 'Moscow_2.jpg', 'Moscow_3.jpg', 'Moscow_4.jpg', 'Moscow_5.jpg'],
          'Saint Peterburg': ['Piter_1.jpg', 'Piter_2.jpg', 'Piter_3.jpg', 'Piter_4.jpg', 'Piter_5.jpg'],
          'Sochi': ['Sochi_1.jpg', 'Sochi_2.jpg', 'Sochi_3.jpg', 'Sochi_4.jpg', 'Sochi_5.jpg'],
          'Kazan': ['Kazan_1.jpg', 'Kazan_2.jpg', 'Kazan_3.jpg'],
          'Ekaterenburg': ['Ekb_1.jpg', 'Ekb_2.jpg', 'Ekb_3.jpg'],
          'Arhangelsk': ['Arhangelsk_1.jpg', 'Arhangelsk_2.jpg']}

NAME_TOWNS = {'Moscow': ["Москва", 'москва'],
              'Saint Peterburg': ['Санкт-Петербург', "спб", "Спб", "СПБ", "питер", "Питер", "санкт петербург",
                                  "Санкт петербург", "Санкт Петербург", "санкт-петербург", "Санкт-петербург"],
              'Sochi': ['Сочи', 'сочи'],
              'Kazan': ["Казань", "казань"],
              'Ekaterenburg': ["Екатеринбург", "екатеринбург", "Екб", "ЕКБ", "екб"],
              'Arhangelsk': ['Архангельск', 'архангельск']}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

reply_keyboard = [['🎮 играть 🎮', '⚙️ настройки ⚙️'], ['📊 статистика 📊', '📖 информация 📖']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False)


async def start(update, context):
    if str(update.message.chat.id) not in DATA:
        await update.message.reply_text("Я бот-игра! Используйте команды для старта игры!", reply_markup=markup)
        await edit_data(update, context, 'new')
    else:
        await update.message.reply_text("Бот уже запущен! Используйте команды для старта игры!", reply_markup=markup)
    return context


async def edit_data(update, context, command):
    global DATA
    if command == 'new':
        DATA[str(update.message.chat.id)] = ['easy', '0']
    elif command in ["лёгкая", "средняя", "сложная", "смешанная"]:
        user_id = str(update.callback_query.from_user.id)
        DATA[user_id] = [ENWORDS[command], DATA[user_id][1]]
    return context


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Клавиатура закрыта. Испоьзуйте /start для её запуска!",
        reply_markup=ReplyKeyboardRemove())
    return context


async def info(update, context):
    await update.message.reply_text("Информация о боте:\n"
                                    "🎮 играть 🎮 - активирует игру, в которой вам нужно ввести название города,"
                                    " изображённого на картинке, затем оценить игру от 1 до 5.\n"
                                    "⚙️ настройки ⚙️ - выбрать сложность или настройить профиль.\n"
                                    "📊 статистика 📊 - отоброжает вашу статистику.\n"
                                    "📖 информация 📖 - отоброжает информацию о боте.")
    return context


async def stat(update, context):
    await update.message.reply_text(f"У вас {DATA[str(update.message.chat.id)][1]} верных ответов!")
    return context


async def play(update, context):
    hard = DATA[str(update.message.chat.id)][0]
    if hard == 'multy':
        hard = random.choice(['easy', 'medium', 'hard'])
    town = random.choice(TOWNS[hard])
    photo = random.choice(PHOTOS[town])
    await update.message.reply_text(f'Ваша сложность - {RUWORDS[DATA[str(update.message.chat.id)][0]]}')
    await update.message.reply_text("Здравствуйте. Угадайте город по фото:")
    await update.message.reply_photo(rf'Russia cities\{town}\{photo}')
    await update.message.reply_text("Введите название города:")
    context.user_data['true_answer'] = NAME_TOWNS[town]
    context.user_data['isgame'] = 'wait town'


async def first_response(update, context):
    global DATA
    true_answer = context.user_data['true_answer']
    user_answer = update.message.text
    if user_answer in true_answer:
        user_id = str(update.message.chat.id)
        DATA[user_id] = [DATA[user_id][0], str(int(DATA[user_id][1]) + 1)]
        await update.message.reply_text(f'Вы угадали город - {true_answer[0]}')
    else:
        await update.message.reply_text(f'Вы не угадали город {true_answer[0]}, выбрав - {user_answer}')
    await update.message.reply_text('Оцените игру от 1 до 5')
    context.user_data['isgame'] = 'wait number'


async def second_response(update, context):
    await update.message.reply_text(f"Спасибо за участие!")
    del context.user_data['isgame']
    del context.user_data['true_answer']


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
        await query.edit_message_text(text=f"Ваш id: {update.callback_query.from_user.id}")
    elif answer == "закрыть":
        await query.edit_message_text(text="Настройки закрыты")
    elif answer in ["лёгкая", "средняя", "сложная", "смешанная"]:
        await edit_data(update, context, answer)
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

with open('data.txt', 'w') as data:
    for elem in [f'{el}/{DATA[el][0]}/{DATA[el][1]}\n' for el in DATA]:
        data.write(elem)
    print('success exit')
