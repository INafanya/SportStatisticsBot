from datetime import datetime

from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from aiogram.utils.formatting import Text, Bold


router: Router = Router()

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
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None:
        await message.reply(
            "Не передан пробег\n"
            "Пример команды: /newstat <Пробег>"
        )
        return
    try:
        new_run = int(command.args)
    except ValueError:
        await message.reply(
            "Пробег должен быть числом"
        )

    time_now = datetime.now().strftime('%H:%M')
    stat_user_id = message.from_user.id

    await message.reply(
        f"Новый пробег зафиксирован\n"
        f"Итого за сегодня: {new_run} "
    )