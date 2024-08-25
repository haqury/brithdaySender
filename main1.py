import pandas as pd
from datetime import datetime, timedelta
from telegram import Bot
import logging
import asyncio
import pdfplumber
import requests
from dotenv import load_dotenv
import os
import schedule
import time


# Ссылка на производственный календарь
CALENDAR_URL_TEMPLATE = 'https://static.consultant.ru/obj/file/calendar/calendar_{year}.pdf'
CALENDAR_FILE_TEMPLATE = 'production_calendar_{year}.csv'

# Загрузка переменных окружения из .env файла
load_dotenv()
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Чтение файла с днями рождения
birthdays = pd.read_csv('received_file.csv')

# Инициализация бота
bot = Bot(token=TOKEN)

# Функция для загрузки производственного календаря из PDF
def load_production_calendar_from_pdf(url):
    response = requests.get(url)
    pdf = pdfplumber.open(BytesIO(response.content))

    # Предполагаем, что календарь находится на первой странице
    page = pdf.pages[0]
    text = page.extract_text()

    # Парсим текст в DataFrame (этот шаг может требовать корректировки в зависимости от структуры PDF)
    data = []
    lines = text.split('\n')
    for line in lines:
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:  # Предполагаем, что строка содержит дату и статус дня
                date_str = parts[0]
                is_workday = 'рабочий' in parts[1:]
                date = datetime.strptime(date_str, '%d.%m.%Y')
                data.append((date, is_workday))

    calendar_df = pd.DataFrame(data, columns=['date', 'is_workday'])
    return calendar_df


# Функция для сохранения календаря в CSV
def save_calendar_to_csv(calendar_df, filename):
    calendar_df.to_csv(filename, index=False)


# Функция для загрузки производственного календаря из CSV
def load_production_calendar_from_csv(filename):
    return pd.read_csv(filename, parse_dates=['date'])


# Функция для загрузки календаря (из файла или из интернета)
def load_production_calendar():
    current_year = datetime.now().year
    calendar_file = CALENDAR_FILE_TEMPLATE.format(year=current_year)
    calendar_url = CALENDAR_URL_TEMPLATE.format(year=current_year)

    if os.path.exists(calendar_file):
        return load_production_calendar_from_csv(calendar_file)
    else:
        calendar_df = load_production_calendar_from_pdf(calendar_url)
        save_calendar_to_csv(calendar_df, calendar_file)
        return calendar_df


# Функция для проверки, является ли день рабочим
def is_workday(date, calendar):
    day_info = calendar[calendar['date'] == date]
    if not day_info.empty:
        return day_info.iloc[0]['is_workday']
    return False


# Функция для получения списка нерабочих дней до текущей даты
def get_non_workdays_before(date, calendar):
    non_workdays = []
    prev_date = date - timedelta(days=1)
    while not is_workday(prev_date, calendar):
        non_workdays.append(prev_date)
        prev_date -= timedelta(days=1)
    return non_workdays


# Функция для отправки сообщений
async def send_message(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logging.error(f"Failed to send message to {CHAT_ID}: {e}")


# Основная функция для проверки и отправки поздравлений
async def check_and_send_birthdays():
    today = datetime.today().date()
    calendar = load_production_calendar()

    if is_workday(today, calendar):
        non_workdays = get_non_workdays_before(today, calendar)
        for non_workday in non_workdays:
            previous_day = non_workday.strftime('%m-%d')
            for index, row in birthdays.iterrows():
                if datetime.strptime(row['birthday'], '%Y-%m-%d').strftime('%m-%d') == previous_day:
                    await send_message(row['message'])

        today_str = today.strftime('%m-%d')
        for index, row in birthdays.iterrows():
            if datetime.strptime(row['birthday'], '%Y-%m-%d').strftime('%m-%d') == today_str:
                await send_message(row['message'])

async def main():
    await check_and_send_birthdays()

# Функция для запуска задачи по расписанию
def job():
    asyncio.run(main())

# Планирование задачи
schedule.every().day.at("19:50").do(job)

# Основной цикл
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        print(time.strftime("%H:%M:%S"))  # Вывод текущего времени
        time.sleep(60)  # Подождать 60 секунд перед следующей проверкой
