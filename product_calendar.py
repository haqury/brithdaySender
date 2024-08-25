from datetime import datetime, timedelta
from isdayoff import DateType, ProdCalendar
import dateparser

# Ссылка на производственный календарь
CALENDAR_URL_TEMPLATE = 'https://static.consultant.ru/obj/file/calendar/calendar_{year}.pdf'
CALENDAR_FILE_TEMPLATE = 'production_calendar_{year}.csv'


def get_sends(birthdays, days):
    rows = dict()
    for index, row in birthdays.iterrows():
        parsed_date = dateparser.parse(row['birthday'])
        for day in days:
            if parsed_date.strftime('%m-%d') == day.strftime('%m-%d'):
                if day.strftime('%m-%d') not in rows:
                    rows[day.strftime('%m-%d')] = []
                rows[day.strftime('%m-%d')].append(row)

    return rows


async def get_sand_days(today):
    calendar = ProdCalendar(locale='ru')
    previous_weekends = []

    for day_offset in range(1, 14):
        date = today - timedelta(days=day_offset)
        try:
            if await calendar.date(date) == DateType.WORKING:
                break
            else:
                previous_weekends.append(date)
        except:
            if await calendar.date(date) == DateType.WORKING:
                break
            else:
                previous_weekends.append(date)
    previous_weekends.reverse()
    return previous_weekends
