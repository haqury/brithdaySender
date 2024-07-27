# 0 9 * * * /usr/bin/python3 /path/to/your/birthday_bot.py
import os

import pandas as pd
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv
import logging
import asyncio

load_dotenv()

# Вставьте свой токен Telegram-бота
token = os.getenv('TOKEN')
chat_id = os.getenv('CHAT_ID')

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Чтение файла с днями рождения
birthdays = pd.read_csv('birthdays.csv')

# Инициализация бота
bot = Bot(token=token)

# Асинхронная функция для проверки дней рождения и отправки поздравлений
async def check_and_send_birthdays():
    today = datetime.today().strftime('%m-%d')
    for index, row in birthdays.iterrows():
        if datetime.strptime(row['birthday'], '%Y-%m-%d').strftime('%m-%d') == today:
            message = row['message']
            await bot.send_message(chat_id=chat_id, text=message)

# Основная функция для выполнения проверки
async def main():
    await check_and_send_birthdays()

# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())
