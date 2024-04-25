# Импортируем необходимые классы.
import logging
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters
import requests
import sys
import random

with open('goroda.txt', encoding='utf-8') as txt:
    TOWNS = txt.readlines()

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

reply_keyboard = [['/play', '/stat'],
                  ['/help', '/close']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


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


# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.

# Напишем соответствующие функции.
# Их сигнатура и поведение аналогичны обработчикам текст
async def start(update, context):
    await update.message.reply_text(
        "Я бот-игра! Используйте команды для старта игры!",
        reply_markup=markup
    )


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Клавиатура закрыта. Испоьзуйте /start для её запуска!",
        reply_markup=ReplyKeyboardRemove()
    )


async def helpp(update, context):
    await update.message.reply_text(
        "Я бот, команда в разработке.")


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

    # Число-ключ в словаре states —
    # втором параметре ConversationHandler'а.
    return 1
    # Оно указывает, что дальше на сообщения от этого пользователя
    # должен отвечать обработчик states[1].
    # До этого момента обработчиков текстовых сообщений
    # для этого пользователя не существовало,
    # поэтому текстовые сообщения игнорировались.


async def stat(update, context):
    await update.message.reply_text("В разработке.")


async def first_response(update, context):
    # Сохраняем ответ в словаре.
    context.user_data['locality'] = context.user_data['locality'] + [update.message.text]
    s = context.user_data['locality']
    cords2 = search(context.user_data['locality'][2])
    await update.message.reply_text(f'Вы угадали '
                                    f'город - {s[0]}' if cords2 == s[1] else f'Вы не угадал'
                                                                             f'и город {s[0]}, выбрав - {s[2]}')
    return 2


# Добавили словарь user_data в параметры.
async def second_response(update, context):
    await update.message.reply_text(f"Спасибо за участие! Статистика в разработке!")
    context.user_data.clear()  # очищаем словарь с пользовательскими данными
    return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    application = Application.builder().token('7198751024:AAF8hG5IUJq-BNMJ6BQ0FtH6kQgUDdT7C7I').build()
    application.add_handler(CommandHandler("stat", stat))
    application.add_handler(CommandHandler("help", helpp))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("close", close_keyboard))

    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('play', play)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)]

        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
