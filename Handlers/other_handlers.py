from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from aiogram.utils.formatting import Text, Bold
from Handlers.db_handler import *

router: Router = Router()


# Обработчик сообщения команды /start
@router.message(F.chat.type == "private", CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, <b>{message.from_user.full_name}</b>!\n"
                         f"Личная статистика:\n /mystat")


# Действие при добавлении нового участника чата
@router.message(F.new_chat_members)
async def chat_user_added(message: Message):
    for user in message.new_chat_members:
        content = Text(
            "Привет, ",
            Bold(user.full_name),
            "Справка по боту: /help"
        )
        await message.reply(
            **content.as_kwargs()
        )


# Обработчик команды добавления новой статистики /newstat
@router.message(F.chat.type == "supergroup", Command("newstat"))
async def cmd_add_statistics(
        message: Message,
        command: CommandObject
):
    # Объявляем переменные:
    telegram_id = message.from_user.id

    # Обработка ошибок ввода пробега
    try:
        new_mileage = float(command.args)
    except ValueError:
        await message.reply(
            "Укажите пробег числом"
        )
        return
    except TypeError:
        await message.reply(
            "Укажите пробег"
        )
        return

    if new_mileage > 200:
        await message.reply(
            "Обманщик!"
        )
        return

    day_mileage = update_day_data_db(telegram_id, new_mileage)
    await message.reply(
        f"Новый пробег зафиксирован\n"
        f"Итого за сегодня: {day_mileage} "
    )


# обработчика команды /help
@router.message(F.chat.type == "supergroup", Command("help"))
async def cmd_help(
        message: Message,
):
    await message.reply(
        f"Добавление пробега:\n"
        f"/newstat км.км\n"
        f"Уменьшение пробега:\n"
        f"/newstat -pythonкм.км\n"
        f"Личная статистика:\n"
        f"/mystat"
    )


# обработчика команды /mystat
@router.message(Command("mystat"))
async def cmd_user_statistics(
        message: Message,
        bot: Bot
):
    telegram_id = message.from_user.id
    userstat = read_user_satistics_db(telegram_id)
    day_mileage, week_mileage, month_mileage, total_mileage = userstat

    await bot.send_message(telegram_id,
                           f"Твоя статистика бега:\n"
                           f"Дневной пробег: <b>{day_mileage}</b> км.\n"
                           f"Недельный пробег: <b>{week_mileage}</b> км.\n"
                           f"Месячный пробег: <b>{month_mileage}</b> км.\n"
                           f"Общий пробег: <b>{total_mileage}</b> км."
                           )


@router.message(Command("test"))
async def cmd_test(message: Message, bot: Bot):
    telegram_id = message.from_user.id

    await bot.send_message(telegram_id, 'test')
