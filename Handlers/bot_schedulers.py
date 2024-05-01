# Таймеры

import schedule
import time
from Handlers.db_handler import clear_day_mileage, clear_week_mileage, clear_month_mileage


def bot_schedulers():
    # суточный таймер. Обнуляет дневной пробег в 23:59
    schedule.every().day.at("23:59").do(clear_day_mileage)

    # недельный таймер. Обнуляет недельный пробег в воскресенье в 23:59
    schedule.every().sunday.at("23:59").do(clear_week_mileage)

    # месячный таймер. Обнуляет месячный пробег в конце месяца???
    schedule.every(4).sunday.at("23:59").do(clear_month_mileage)
    while True:
        schedule.run_pending()
        time.sleep(1)