from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
import asyncio
from dotenv import load_dotenv
import os
import schedule
import time
import pandas as pd
from datetime import datetime

# Загрузка переменных окружения из .env файла
load_dotenv()
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Инициализация бота
bot = Bot(token=TOKEN)

# Чтение файла с днями рождения
birthdays = pd.DataFrame()  # Изначально пустой DataFrame


def update_birthdays_from_file(file_path):
    global birthdays
    try:
        # Загрузка данных из CSV файла
        birthdays = pd.read_csv(file_path)
        logging.info(f"Файл загружен: {file_path}")
    except Exception as e:
        logging.error(f"Ошибка при обработке файла {file_path}: {e}")


async def check_and_send_birthdays():
    today = datetime.today().strftime('%m-%d')
    if birthdays.empty:
        logging.info("Нет данных для обработки.")
        return

    for index, row in birthdays.iterrows():
        if datetime.strptime(row['birthday'], '%Y-%m-%d').strftime('%m-%d') == today:
            message = row['message']
            try:
                await bot.send_message(chat_id=CHAT_ID, text=message)
            except Exception as e:
                logging.error(f"Failed to send message to {CHAT_ID}: {e}")


async def main():
    await check_and_send_birthdays()


def job():
    asyncio.run(main())


# Планирование задачи
schedule.every().day.at("17:43").do(job)  # Выполнять ежедневно в 09:00


# Функции для обработки команд и файлов
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Привет! Отправьте мне CSV файл с днями рождения.')


async def handle_document(update: Update, context: CallbackContext):
    file = update.message.document.get_file()
    file.download('received_file.csv')
    await update.message.reply_text('Файл успешно загружен и сохранен.')

    # Обновление данных из загруженного файла
    update_birthdays_from_file('received_file.csv')


# Основной код для запуска бота
def run_bot():
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    # Запуск планировщика задач в отдельном потоке
    import threading

    threading.Thread(target=lambda: schedule.run_pending()).start()

    # Запуск бота
    run_bot()

    # Основной цикл для планировщика задач
    while True:
        schedule.run_pending()
        time.sleep(60)  # Подождать 60 секунд перед следующей проверкой
