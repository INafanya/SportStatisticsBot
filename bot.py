import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Handlers.db_handler import create_sql_db, copy_day_club_mileage
from Handlers.db_handler import copy_and_clear_day_mileage, copy_and_clear_week_mileage
from Config.config_reader import config
from aiogram import Bot, Dispatcher
from Handlers import other_handlers
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from Handlers.other_handlers import show_day_rating, show_week_rating, show_club_mileage_rating

# Инициализация логирования
logger = logging.getLogger(__name__)

dp = Dispatcher()


async def main() -> None:
    # конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
        filename="bot_log.log",
        filemode="w"
    )

    # Выводим в консоль старт бота
    logger.info('Starting SportStatisticBot...')

    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(
        token=config.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Регистрируем обработчики(handlers)
    dp.include_router(other_handlers.router)

    # Инициализируем планировщик
    scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    # Суточный таймер. Обнуляет дневной пробег каждый день в 23:55
    scheduler.add_job(copy_and_clear_day_mileage, 'cron', hour=23, minute=55)
    # Суточный таймер. копирует суммарный пробег по клубам в БД
    # scheduler.add_job(copy_day_club_mileage, 'cron', hour=23, minute=57)
    # Суточный таймер. Выводит вчерашний рейтинг
    # scheduler.add_job(show_day_rating, 'cron', hour=8, minute=1, args=(bot,))
    # Суточный таймер. Выводит вчерашний рейтинг по клубам
    # scheduler.add_job(show_club_mileage_rating, 'cron', hour=8, minute=0, args=(bot,))

    # Недельный таймер. Обнуляет недельный пробег каждое воскресенье в 23:56
    scheduler.add_job(copy_and_clear_week_mileage, 'cron', day_of_week='sun', hour=23, minute=56)
    # Суточный таймер. Выводит рейтинг за прошедшую неделю
    # scheduler.add_job(show_week_rating, 'cron', day_of_week='mon', hour=8, minute=2, args=(bot,))

    # 4-х недельный таймер. Обнуляет и копирует пробег в каждое 4-е воскресенье в 23:58
    # scheduler.add_job(copy_and_clear_month_mileage, 'cron', day='last sun', hour=23, minute=58)

    # scheduler.add_job(show_month_mileage, 'cron', day='first mon', hour=8, minute=2)

    # месячный таймер. Обнуляет месячный пробег в последний день месяца в 23:58
    # scheduler.add_job(copy_and_clear_month_mileage, 'cron', month='*', day='last', hour=23, minute=58)

    scheduler.start()
    # проверяем на наличие БД
    logger.info("Проверка наличия БД")
    create_sql_db()

    # Пропускаем накопившиеся апдейты телеги и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
