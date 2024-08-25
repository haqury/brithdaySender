# 0 9 * * * /usr/bin/python3 /path/to/your/birthday_bot.py
import locale
import os

import pandas as pd
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv
import logging
import asyncio
import product_calendar
import re

load_dotenv()

# Вставьте свой токен Telegram-бота
token = os.getenv('TOKEN')
chat_id = os.getenv('CHAT_ID')

logger = logging.getLogger(__name__)

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Чтение файла с днями рождения
birthdays = pd.read_csv('received_file.csv')
templates = pd.read_csv('templates.csv')

# Инициализация бота
bot = Bot(token=token)


def replace_variables(message, data):
    # Функция, которая будет заменять найденные шаблоны на соответствующие значения
    def replacer(match):
        # Извлекаем ключ из совпадения
        key = match.group(1)
        # Возвращаем значение из словаря, если ключ существует, иначе оставляем шаблон как есть
        return data.get(key, match.group(0))

    # Ищем все шаблоны в формате {{attr}} и заменяем их
    return re.sub(r'{{(\w+)}}', replacer, message)


async def send_for_month(recivers_for_month, date):
    locale.setlocale(locale.LC_TIME, 'ru_RU')
    m = date.strftime('%B')
    message = replace_variables(templates['default_header_list_for_month'][0], {'month': m})
    for row in recivers_for_month:
        message = message + '\n\n' + replace_variables(templates['default_line_for_month'][0], row)

    await bot.send_message(chat_id=chat_id, text=message)
    return


async def send_birthdays(recivers, date):
    for idate, rows in recivers.items():
        if idate == date:
            day = 'сегодня'
        else:
            locale.setlocale(locale.LC_TIME, 'ru_RU')
            day = datetime.strptime(idate, '%m-%d').strftime('%d %B')

        message = replace_variables(templates['default_header_message'][0], {'currentDay': day}) + '\n\n'
        for row in rows:
            message = message + '\n' + replace_variables(templates['default_message'][0], row)

        await bot.send_message(chat_id=chat_id, text=message)


# Асинхронная функция для проверки дней рождения и отправки поздравлений
async def check_and_send_birthdays(date=datetime.now()):
    date = datetime.strptime('2024-01-08', '%Y-%m-%d')
    days = await product_calendar.get_sand_days(date)
    recivers_for_month = product_calendar.get_recived_for_month(birthdays, date.strftime('%m'))

    for day in days:
        if day.strftime('%d') == '01':
            await send_for_month(recivers_for_month, date)

    recivers = product_calendar.get_sends(birthdays, days)
    await send_birthdays(recivers, date)


# Основная функция для выполнения проверки
async def main():
    await check_and_send_birthdays()


# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())
