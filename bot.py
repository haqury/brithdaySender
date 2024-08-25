import logging
import pandas as pd
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext
from dotenv import load_dotenv
import os
import openai

# Загрузка переменных окружения из .env файла
load_dotenv()
TOKEN = os.getenv('TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Настройка OpenAI
openai.api_key = OPENAI_API_KEY

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Инициализация DataFrame для дней рождения
birthdays = pd.DataFrame(columns=['birthday', 'message'])


# Загрузка дней рождения из CSV файла
def load_birthdays():
    global birthdays
    if os.path.exists('received_file.csv'):
        birthdays = pd.read_csv('received_file.csv')


# Сохранение дней рождения в CSV файл
def save_birthdays():
    global birthdays
    birthdays.to_csv('received_file.csv', index=False)

# Функция для обработки полученного файла
async def receive_file(update: Update, context: CallbackContext):
    file = await context.bot.get_file(update.message.document.file_id)
    file_path = os.path.join(os.getcwd(), update.message.document.file_name)
    await file.download_to_drive(file_path)

    load_birthdays()
    await update.message.reply_text(f"Файл '{update.message.document.file_name}' успешно получен и сохранен!")
    save_birthdays()

# Функция для обработки текстовых сообщений и сохранения их в файл
async def receive_message(update: Update, context: CallbackContext):
    text = update.message.text
    with open("received_messages.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")
    await update.message.reply_text("Сообщение успешно получено и сохранено!")

# Основной блок
if __name__ == "__main__":
    # Инициализация Application
    application = Application.builder().token(TOKEN).build()

    # Настройка обработчиков
    file_handler = MessageHandler(filters.Document.ALL, receive_file)

    application.add_handler(file_handler)

    # Запуск бота
    application.run_polling()
