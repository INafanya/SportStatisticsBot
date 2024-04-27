import asyncio
import logging
import sys
from Config.config_reader import config
from aiogram import Bot, Dispatcher
from Handlers import other_handlers
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Инициализация логирования
logger = logging.getLogger(__name__)

dp = Dispatcher()

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:@(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s'
    )
    # Выводим в консоль старт бота
    logger.info('Starting bot_name...')

    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(
        token=config.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    # And the run events dispatching
    await dp.start_polling(bot)

    # Регистрируем обработчики(handlers)
    dp.include_routers(other_handlers.router)

    # Пропускаем накопившиеся апдейты телеги
    await bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())