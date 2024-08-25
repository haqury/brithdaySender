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

# Асинхронная функция для проверки дней рождения и отправки поздравлений
async def check_and_send_birthdays(date = datetime.now()):
    templates = pd.read_csv('templates.csv')
    days = await product_calendar.get_sand_days(datetime.strptime('2024-01-08','%Y-%m-%d'))
    recivers = product_calendar.get_sends(birthdays, days)

    for idate, rows in recivers.items():
        if idate == date:
            day = 'сегодня'
        else:
            locale.setlocale(locale.LC_TIME, 'ru_RU')
            day = datetime.strptime(idate, '%m-%d').strftime('%d %B')

        message = replace_variables(templates['default_header_message'][0], {'currentDay': day})
        for row in rows:
            message = message + '\n' + replace_variables(templates['default_message'][0], row)

        await bot.send_message(chat_id=chat_id, text=message)

# Основная функция для выполнения проверки
async def main():
    await check_and_send_birthdays()

# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())
