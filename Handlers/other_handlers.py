from aiogram import Router, F
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

    if new_mileage > 100:
        await message.reply(
            "Обманщик!"
        )
        return

    day_mileage = update_day_data_db(telegram_id, new_mileage)
    await message.reply(
        f"Новый пробег зафиксирован\n"
        f"Итого за сегодня: {day_mileage} "
    )
