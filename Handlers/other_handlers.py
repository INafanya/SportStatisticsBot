from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from aiogram.utils.formatting import Text, Bold


router: Router = Router()

#Словарь для хранения пробега(сбрасывается при перезапуске бота)
mileage_data = {}

def add_mileage_data(
        telegram_id: int,
        new_mileage: float
        #week_mileage: float,
        #month_mileage: float,
        #total_mileage: float
):
    if telegram_id in mileage_data:
        mileage_data[telegram_id] += new_mileage
    else:
        mileage_data[telegram_id] = new_mileage

# Обработчик сообщения команды /start
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, <b>{message.from_user.full_name}</b>! Твой ID: {message.from_user.id}")

# Действие при добавлении нового участника чата
@router.message(F.new_chat_members)
async def chat_user_added(message: Message):
    for user in message.new_chat_members:
        content = Text(
            "Привет, ",
            Bold(user.full_name)
        )
        # проперти full_name берёт сразу имя И фамилию
        await message.reply(
            **content.as_kwargs()
        )

# Обработчик команды добавления новой статистики /add_stat
@router.message(Command("newstat"))
async def cmd_add_statistics(
        message: Message,
        command: CommandObject
    ):

    # Объявляем переменные:

    time_now = datetime.now().strftime('%H:%M')
    telegram_id = message.from_user.id

    # Обработка ошибок ввода пробега
    try:
        new_mileage = float(command.args)
    except ValueError:
        await message.reply(
            "Укажите пробег числом"
        )
    except TypeError:
        await message.reply(
            "Укажите пробег"
        )

    if new_mileage > 100:
        await message.reply(
            "Обманщик!"
        )
        return
    add_mileage_data(telegram_id, new_mileage)
    await message.reply(
        f"Новый пробег зафиксирован\n"
        f"Итого за сегодня: {mileage_data[telegram_id]} "
    )
