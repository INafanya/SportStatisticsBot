from datetime import datetime
from time import strftime

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, user
from aiogram.utils.formatting import Text, Bold
from Handlers.db_handler import *
from Config.config_reader import admin

router: Router = Router()

chat_id = -1002119719477


# Обработчик сообщения команды /start
@router.message(F.chat.type == "private", CommandStart())
async def command_start_handler(message: Message) -> None:
    if message.from_user.id in admin:
        await message.answer(f"Привет, <b>{message.from_user.full_name}</b>!\n"
                             f"Личная статистика:\n /mystat")
    else:
        await message.answer(f"Эта команда для админа!")


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
    username = message.from_user.full_name
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

    day_mileage = update_day_data_db(telegram_id, username, new_mileage)
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
        f"/newstat -км.км\n"
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
    user_statistics = read_user_statistics_db(telegram_id)
    if user_statistics:
        username, day_mileage, week_mileage, month_mileage, total_mileage = user_statistics

        await bot.send_message(telegram_id,
                               f"Твоя статистика бега:\n"
                               f"Дневной пробег: <b>{day_mileage}</b> км.\n"
                               f"Недельный пробег: <b>{week_mileage}</b> км.\n"
                               f"Месячный пробег: <b>{month_mileage}</b> км.\n"
                               f"Общий пробег: <b>{total_mileage}</b> км."
                               )
    else:
        await bot.send_message(telegram_id,
                               f"Сначала добавь пробег"
                               )


# отправка дневного рейтинга в общий чат

@router.message(F.chat.type == "supergroup", Command("day"))
async def cmd_day_rating(
        message: Message,
        bot: Bot
):
    try:
        day_now = datetime.now()
        day_rating = read_day_rating()
        text_answer = ""

        if len(day_rating) == 1:
            print(len(day_rating))
            print(day_rating)

            for (index, i) in enumerate(day_rating):
                text_answer += f"{index + 1}. {day_rating[0][index][1]} - {day_rating[0][index][2]} км.\n"
            print(text_answer)

        else:
            winners, loosers, users_summ = read_day_rating()
            loosers_index = users_summ[0][0] - 2

            for (index, i) in enumerate(winners):
                text_answer += f"{index + 1}. {winners[index][1]} - {winners[index][2]} км.\n"

            text_answer += f"...\n"

            for (index, i) in enumerate(loosers):
                text_answer += f"{loosers_index}. {loosers[index][1]} - {loosers[index][2]} км.\n"
                loosers_index += 1
    except IndexError:
        text_answer = f'Нет пробега за эту дату'

    await bot.send_message(chat_id, f"#Итог дня {day_now.strftime('%d.%m.%Y')}\n"
                                    f"\n"
                                    f"{text_answer}"

                           )


@router.message(F.chat.type == "supergroup", Command("test"))
async def cmd_day_rating_test(
        message: Message,
        bot: Bot
):
    try:
        day_now = datetime.now()
        day_rating = read_day_rating()
        text_answer = ""

        if len(day_rating) == 1:
            print(len(day_rating))
            print(day_rating)

            for (index, i) in enumerate(day_rating):
                text_answer += f"{index + 1}. {day_rating[0][index][1]} - {day_rating[0][index][2]} км.\n"
            print(text_answer)

        else:
            winners, loosers, users_summ = read_day_rating()
            loosers_index = users_summ[0][0] - 2

            for (index, i) in enumerate(winners):

                text_answer += f"{index + 1}. {winners[index][1]} - {winners[index][2]} км.\n"

            text_answer += f"...\n"

            for (index, i) in enumerate(loosers):

                text_answer += f"{loosers_index}. {loosers[index][1]} - {loosers[index][2]} км.\n"
                loosers_index += 1
    except IndexError:
        text_answer = f'Нет пробега за эту дату'

    await bot.send_message(chat_id, f"#Итог дня {day_now.strftime('%d.%m.%Y')}\n"
                                    f"\n"
                                    f"{text_answer}"

                           )
'''
    day_rating = read_day_rating()
    day_now = datetime.now()
    users_summ = day_rating[-1][0] - 3
    text_answer = ""

    for (index, i) in enumerate(day_rating):
        if len(day_rating) - 1 >= index >= len(day_rating) - 4:
            break
        text_answer += f"{index + 1}. {day_rating[index][1]} - {day_rating[index][2]} км.\n"

    for (index, i) in enumerate(day_rating):
        if len(day_rating) - 1 > index >= len(day_rating) - 4:
            text_answer += f"{index + 1}. {day_rating[index][1]} - {day_rating[index][2]} км.\n"

    await bot.send_message(chat_id, f"#Итог дня {day_now.strftime('%d.%m.%Y')}\n"
                                    f"\n"
                                    f"{text_answer}"

                           )
'''