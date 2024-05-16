import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Handlers.db_handler import create_sql_db
from Handlers.db_handler import copy_and_clear_day_mileage, copy_and_clear_week_mileage, copy_and_clear_month_mileage
from Config.config_reader import config, chat_id
from aiogram import Bot, Dispatcher
from Handlers import other_handlers
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Handlers.db_handler import create_sql_db
from Handlers.db_handler import copy_and_clear_day_mileage, copy_and_clear_week_mileage, copy_and_clear_month_mileage
from Config.config_reader import config, chat_id
from aiogram import Bot, Dispatcher
from Handlers import other_handlers
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from Handlers.other_handlers import show_day_rating, cmd_week_rating, show_week_rating

# Инициализация логирования
logger = logging.getLogger(__name__)

dp = Dispatcher()


async def main() -> None:
    # конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
       # format='%(filename)s:@(lineno)d #%(levelname)-8s '
        #       '[%(asctime)s] - %(name)s - %(message)s'#,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s'
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

    if __name__ == '__main__':
        # Инициализируем планировщик
        scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone="Europe/Moscow")
        # суточный таймер. Обнуляет дневной пробег каждый день в 23:57
        scheduler.add_job(copy_and_clear_day_mileage, 'cron', hour=23, minute=57)

        scheduler.add_job(show_day_rating, 'cron', hour=8, minute=0, args=(bot,))

        # недельный таймер. Обнуляет недельный пробег каждое воскресенье в 23:58
        scheduler.add_job(copy_and_clear_week_mileage, 'cron', day_of_week='sun', hour=23, minute=58)

        #scheduler.add_job(show_week_rating, 'cron', day_of_week='mon', hour=8, minute=5, args=(bot,))


        # месячный таймер. Обнуляет месячный пробег в последний день месяца в 23:58
        #переделать под 4-х недельный таймер
        scheduler.add_job(copy_and_clear_month_mileage, 'cron', month='*', day='last', hour=23, minute=54)

        scheduler.start()
    # проверяем на наличие БД
    print("Проверка наличия БД")
    create_sql_db()

    # Пропускаем накопившиеся апдейты телеги и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

from Handlers.other_handlers import show_day_rating, show_week_rating

# Инициализация логирования
logger = logging.getLogger(__name__)

dp = Dispatcher()


async def main() -> None:
    # конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
       # format='%(filename)s:@(lineno)d #%(levelname)-8s '
        #       '[%(asctime)s] - %(name)s - %(message)s'#,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s'
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

    if __name__ == '__main__':
        # Инициализируем планировщик
        scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone="Europe/Moscow")
        # суточный таймер. Обнуляет дневной пробег каждый день в 23:54
        scheduler.add_job(copy_and_clear_day_mileage, 'cron', hour=23, minute=54)

        scheduler.add_job(show_day_rating, 'cron', hour=8, minute=0, args=(bot,))

        # недельный таймер. Обнуляет недельный пробег каждое воскресенье в 23:56
        scheduler.add_job(copy_and_clear_week_mileage, 'cron', day_of_week='sun', hour=23, minute=56)
        scheduler.add_job(show_week_rating, 'cron', day_of_week='mon', hour=8, minute=5, args=(bot,))

        # месячный таймер. Обнуляет месячный пробег в последний день месяца в 23:58
        # переделать под 4-х недельный таймер
        scheduler.add_job(copy_and_clear_month_mileage, 'cron', month='*', day='last', hour=23, minute=58)

        scheduler.start()
    # проверяем на наличие БД
    print("Проверка наличия БД")
    create_sql_db()

    # Пропускаем накопившиеся апдейты телеги и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
