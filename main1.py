import pandas as pd
from datetime import datetime
from telegram import Bot
import logging
import asyncio
from dotenv import load_dotenv
import os
import schedule
import time

# Загрузка переменных окружения из .env файла
load_dotenv()
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Чтение файла с днями рождения
birthdays = pd.read_csv('birthdays.csv')

# Инициализация бота
bot = Bot(token=TOKEN)

async def check_and_send_birthdays():
    today = datetime.today().strftime('%m-%d')
    for index, row in birthdays.iterrows():
        # Проверка на совпадение дня рождения с сегодняшним днем
        if datetime.strptime(row['birthday'], '%Y-%m-%d').strftime('%m-%d') == today:
            message = row['message']
            try:
                await bot.send_message(chat_id=CHAT_ID, text=message)
            except Exception as e:
                logging.error(f"Failed to send message to {CHAT_ID}: {e}")

async def main():
    await check_and_send_birthdays()

# Функция для запуска задачи по расписанию
def job():
    asyncio.run(main())

# Планирование задачи
schedule.every().day.at("17:15").do(job)

# Основной цикл
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)  # Подождать 60 секунд перед следующей проверкой
