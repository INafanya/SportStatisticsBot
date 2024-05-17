import os
from datetime import datetime
from aiogram import Router, F, Bot, types
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, FSInputFile
from aiogram.utils.formatting import Text, Bold
from Handlers.db_handler import read_user_statistics_from_db, update_day_data_db, read_day_rating, read_week_rating, \
    get_yesterday, get_yesterweek, export_data_to_file
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
                                  "Справка по боту: /помощь"
                                  "Для начала работы с ботом нажми https://t.me/SportStatistics_bot"
        )
        await message.reply(
            **content.as_kwargs()
        )


# Обработчик команды добавления новой статистики /д
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
        f"Для работы с ботом нажми https://t.me/SportStatistics_bot\n"
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
            f"Твоя статистика бега на {datetime.now().strftime('%d.%m.%Y')}:\n"
            f"\n"
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
async def show_day_rating(bot: Bot
                          ):
    try:
        day_rating = read_day_rating()
        text_answer = ""
        summ_mileage = 0
        winners = ""
        loosers = ""
        yesterday = get_yesterday()
        user_sum = len(day_rating)

        for (index, i) in enumerate(day_rating):
            float_day_rating = round(float(str(day_rating[index][2]).replace(',', '.')), 2)
            summ_mileage += float_day_rating
            if index <= 4:
                winners += f"{index + 1}. {day_rating[index][1]} - {float_day_rating} км.\n"
            elif index >= user_sum - 3:
                loosers += f"...\n" \
                           f"{index + 1}. {day_rating[index][1]} - {float_day_rating} км.\n"
        text_answer = f"{winners}" \
                      f"{loosers}"
    except IndexError:
        text_answer = f'Нет пробега за {yesterday}'

    await bot.send_message(
        chat_id,
        f"#Итог_дня {yesterday}\n"
        f"#Командный_пробег: {round(summ_mileage, 2)}км.\n"
        f"\n"
        f"{text_answer}"
    )


# Отправка дневного рейтинга по команде /day
@router.message(F.chat.type == "supergroup", Command("day"))
async def cmd_day_rating(message: Message, bot: Bot
                         ):
    if message.from_user.id in admin:
        await show_day_rating(bot)
    else:
        await message.answer(f"Эта команда для админа!")



async def show_week_rating(bot: Bot
                           ):
    try:
        week_rating = read_week_rating()
        text_answer = ""
        summ_mileage = 0
        winners = ""
        loosers = ""
        yesterweek = get_yesterweek()
        user_sum = len(week_rating)

        for (index, i) in enumerate(week_rating):
            float_week_rating = round(float(str(week_rating[index][2]).replace(',', '.')), 2)
            summ_mileage += float_week_rating
            if index <= 4:
                winners += f"{index + 1}. {week_rating[index][1]} - {float_week_rating} км.\n"
            elif index >= user_sum - 3:
                loosers += f"...\n" \
                           f"{index + 1}. {week_rating[index][1]} - {float_week_rating} км.\n"
        text_answer = f"{winners}" \
                      f"{loosers}"
    except IndexError:
        text_answer = f'Нет пробега за {yesterweek} неделю'

    await bot.send_message(
        chat_id,
        f"#Рейтинг_недели {yesterweek}\n"
        f"#Командный_пробег: {round(summ_mileage, 2)}км.\n"
        f"\n"
        f"{text_answer}"
    )


@router.message(F.chat.type == "supergroup", Command("week"))
async def cmd_week_rating(message: Message, bot: Bot
                          ):
    if message.from_user.id in admin:
        await show_week_rating(bot)
    else:
        await message.answer(f"Эта команда для админа!")



@router.message(F.chat.type == "private", Command("файл"))
async def cmd_export_data_to_file(
        message: types.Document,
        bot: Bot,
):
    if message.from_user.id in admin:
        filename = export_data_to_file()

        file_to_send = FSInputFile(filename)

        if os.path.exists(filename):
            print("Отправка файла пользователю")
            await bot.send_document(message.from_user.id, file_to_send)
            os.remove(filename)
            print("Файл отправлен")
            print("Файл удалён")
        else:
            await bot.send_message(message.from_user.id, "Файл не найден. Проверьте путь к файлу.")
    else:
        await message.answer(f"Эта команда для админа!")