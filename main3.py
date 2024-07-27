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
send_time = "09:00"  # По умолчанию время отправки


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
            name = row['name']
            message = row.get('message', 'С днем рождения!')
            position = row.get('position', '')
            note = row.get('note', '')
            full_message = f"С днем рождения, {name}! Позиция: {position}. Заметка: {note}\nСообщение: {message}"
            try:
                await bot.send_message(chat_id=CHAT_ID, text=full_message)
            except Exception as e:
                logging.error(f"Failed to send message to {CHAT_ID}: {e}")


async def main():
    await check_and_send_birthdays()


def job():
    asyncio.run(main())


def update_schedule():
    global send_time
    schedule.clear()  # Очистить предыдущие задачи
    schedule.every().day.at(send_time).do(job)  # Установить новое время для задачи


# Планирование задачи
update_schedule()  # Установить начальное время отправки


# Функции для обработки команд и файлов
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Привет! Отправьте мне CSV файл с днями рождения.')


async def handle_document(update: Update, context: CallbackContext):
    document = update.message.document
    if document.mime_type == "text/csv":
        file = document.get_file()
        file.download('received_file.csv')
        await update.message.reply_text('Файл успешно загружен и сохранен.')

        # Обновление данных из загруженного файла
        update_birthdays_from_file('received_file.csv')
    else:
        await update.message.reply_text('Пожалуйста, отправьте файл в формате CSV.')


async def set_time(update: Update, context: CallbackContext):
    global send_time
    if context.args:
        new_time = context.args[0]
        try:
            # Проверка корректности формата времени
            datetime.strptime(new_time, "%H:%M")
            send_time = new_time
            update_schedule()  # Обновить расписание
            await update.message.reply_text(f"Время отправки сообщений обновлено на {send_time}.")
        except ValueError:
            await update.message.reply_text("Неверный формат времени. Используйте HH:MM.")
    else:
        await update.message.reply_text("Пожалуйста, укажите время в формате HH:MM.")


# Основной код для запуска бота
def run_bot():
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('set_time', set_time))
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
