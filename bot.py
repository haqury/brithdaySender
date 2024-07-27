import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Функция для обработки полученного файла
async def receive_file(update: Update, context: CallbackContext):
    file = await context.bot.get_file(update.message.document.file_id)
    file_path = os.path.join(os.getcwd(), update.message.document.file_name)
    await file.download_to_drive(file_path)
    await update.message.reply_text(f"Файл '{update.message.document.file_name}' успешно получен и сохранен!")

# Основной блок
if __name__ == "__main__":
    # Инициализация Application
    application = Application.builder().token(TOKEN).build()

    # Настройка обработчика для получения файлов
    file_handler = MessageHandler(filters.Document.ALL, receive_file)
    application.add_handler(file_handler)

    # Запуск бота
    application.run_polling()
