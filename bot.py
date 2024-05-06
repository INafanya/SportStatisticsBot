import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Handlers.db_handler import clear_day_mileage, clear_week_mileage, clear_month_mileage
from Config.config_reader import config
from aiogram import Bot, Dispatcher
from Handlers import other_handlers
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Инициализация логирования
logger = logging.getLogger(__name__)

dp = Dispatcher()


async def main() -> None:
    # конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:@(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
    )
    # Выводим в консоль старт бота
    logger.info('Starting SportStatisticBot...')

    # Инициализируем планировщик
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    # суточный таймер. Обнуляет дневной пробег каждый день в 23:57
    scheduler.add_job(clear_day_mileage, 'cron', hour=11, minute=00, id='Clear_day')

    # недельный таймер. Обнуляет недельный пробег каждое воскресенье в 23:58
    scheduler.add_job(clear_week_mileage, 'cron', day_of_week='sun', hour=23, minute=58, id='Clear_week')

    # месячный таймер. Обнуляет месячный пробег в последний день месяца в 23:58
    scheduler.add_job(clear_month_mileage, 'cron', month='*', day='last', hour=23, minute=58)

    scheduler.start()

    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(
        token=config.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Регистрируем обработчики(handlers)
    dp.include_router(other_handlers.router)

    # Пропускаем накопившиеся апдейты телеги и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())