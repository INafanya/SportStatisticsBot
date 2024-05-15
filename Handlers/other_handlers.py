from datetime import datetime, timedelta
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from aiogram.utils.formatting import Text, Bold

from Handlers.db_handler import read_user_statistics_from_db, update_day_data_db, read_day_rating, read_week_rating
from Config.config_reader import admin, chat_id

router: Router = Router()


# Обработчик сообщения команды /start
@router.message(F.chat.type == "private", CommandStart())
async def command_start_handler(message: Message) -> None:
    if message.from_user.id in admin:
        await message.answer(f"Привет, <b>{message.from_user.full_name}</b>!\n"
                             f"Личная статистика:\n /стат")
    else:
        await message.answer(f"Эта команда для админа!")


# Действие при добавлении нового участника чата
@router.message(F.new_chat_members)
async def chat_user_added(message: Message):
    for user in message.new_chat_members:
        content = Text(
            "Привет, ",
            Bold(user.full_name), ". "
                                  "Для работы с ботом нажми Start тут: https://t.me/SportStatistics_bot"
                                  "Справка по боту: /помощь"
        )
        await message.reply(
            **content.as_kwargs()
        )


# Обработчик команды добавления новой статистики /newstat
@router.message(F.chat.type == "supergroup", Command("д"))
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

    # пробег число?
    except ValueError:
        await message.reply(
            "Укажите пробег числом"
        )
        return
    # пробег указан после команды?
    except TypeError:
        await message.reply(
            "Укажите пробег"
        )
        return
    # нереальный дневной пробег
    if new_mileage > 200:
        await message.reply(
            "Обманщик!"
        )
        return

    day_mileage = update_day_data_db(telegram_id, username, new_mileage)

    await message.reply(
        f"Новый пробег зафиксирован\n"
        f"Итого за сегодня: {round(day_mileage, 2)} "
    )


# обработчика команды /помощь
@router.message(F.chat.type == "supergroup", Command("помощь"))
async def cmd_help(
        message: Message,
):
    await message.reply(
        f"Бот: https://t.me/SportStatistics_bot\n"
        f"Добавление пробега:\n"
        f"/д км.км\n"
        f"Уменьшение пробега:\n"
        f"/д -км.км\n"
        f"Личная статистика:\n"
        f"/стат"
    )


# обработчика команды /стат
@router.message(Command("стат"))
async def cmd_user_statistics(
        message: Message,
        bot: Bot
):
    telegram_id = message.from_user.id
    user_statistics = read_user_statistics_from_db(telegram_id)

    if user_statistics:
        username, day_mileage, week_mileage, month_mileage, total_mileage = user_statistics

        await bot.send_message(
            telegram_id,
            f"Твоя статистика бега:\n"
            f"Дневной пробег: <b>{round(day_mileage, 2)}</b> км.\n"
            f"Недельный пробег: <b>{round(week_mileage, 2)}</b> км.\n"
            f"Месячный пробег: <b>{round(month_mileage, 2)}</b> км.\n"
            f"Общий пробег: <b>{round(total_mileage, 2)}</b> км."
        )
    else:
        await bot.send_message(
            telegram_id,
            f"Сначала добавь пробег"
        )


# отправка дневного рейтинга в общий чат

# @router.message(F.chat.type == "supergroup", Command("day"))
async def show_day_rating(bot: Bot
                          ):
    try:
        day_rating = read_day_rating()
        text_answer = ""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%d.%m.%Y')
        if len(day_rating) == 1:

            for (index, i) in enumerate(day_rating[0]):
                float_day_rating = round(float(str(day_rating[0][index][2]).replace(',', '.')), 2)
                text_answer += f"{index + 1}. {day_rating[0][index][1]} - {float_day_rating} км.\n"

        else:
            winners, loosers, users_summ = read_day_rating()
            loosers_index = users_summ[0][0] - 2

            for (index, i) in enumerate(winners):
                float_winners = round(float(str(winners[index][2]).replace(',', '.')), 2)
                text_answer += f"{index + 1}. {winners[index][1]} - {float_winners} км.\n"

            text_answer += f"...\n"

            for (index, i) in enumerate(loosers):
                float_looser = round(float(str(loosers[index][2]).replace(',', '.')), 2)
                text_answer += f"{loosers_index}. {loosers[index][1]} - {float_looser} км.\n"
                loosers_index += 1

    except IndexError:
        text_answer = f'Нет пробега за {yesterday}'

    await bot.send_message(
        chat_id,
        f"#Итог дня {yesterday}\n"
        f"\n"
        f"{text_answer}"
    )


@router.message(F.chat.type == "supergroup", Command("day"))
async def cmd_day_rating(message: Message, bot: Bot
                         ):
    await show_day_rating(bot)


async def show_week_rating(
        bot: Bot
                           ):
    try:
        week_rating = read_week_rating()
        text_answer = ""

        if len(week_rating) == 1:

            for (index, i) in enumerate(week_rating[0]):
                text_answer += f"{index + 1}. {week_rating[0][index][1]} - {week_rating[0][index][2]} км.\n"

        else:
            winners, loosers, users_summ = read_week_rating()
            loosers_index = users_summ[0][0] - 2

            for (index, i) in enumerate(winners):
                text_answer += f"{index + 1}. {winners[index][1]} - {winners[index][2]} км.\n"

            text_answer += f"...\n"

            for (index, i) in enumerate(loosers):
                text_answer += f"{loosers_index}. {loosers[index][1]} - {loosers[index][2]} км.\n"
                loosers_index += 1

    except IndexError:
        text_answer = f'Нет пробега за прошлую неделю'

    await bot.send_message(
        chat_id,
        f"#Итог прошлой недели {(datetime.now() - timedelta(days=7)).strftime('%V')}\n"
        f"\n"
        f"{text_answer}"
    )

@router.message(F.chat.type == "supergroup", Command("week"))
async def cmd_week_rating(message: Message, bot: Bot
                         ):
    await show_week_rating(bot)

@router.message(F.chat.type == "supergroup", Command("test"))
async def cmd_day_rating_test(
        message: Message,
        bot: Bot
):
    try:
        day_now = datetime.now()
        day_rating = read_day_rating()
        text_answer = ""

        print(f" len_day_rating[0]: {len(day_rating[0])}")
        print(f" day_rating: {day_rating}")
        print(f" day_rating[0]: {day_rating[0]}")

        if len(day_rating) == 1:
            for (index, i) in enumerate(day_rating[0]):
                text_answer += f"{index + 1}. {day_rating[0][index][1]} - {day_rating[0][index][2]} км.\n"
            print(text_answer)

        else:
            winners, loosers, users_summ = day_rating[0]
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
