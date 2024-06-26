import os
from datetime import datetime
from aiogram import Router, F, Bot, types
from aiogram.filters import CommandStart, Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.utils.formatting import Text, Bold
from Handlers.db_handler import read_user_statistics_from_db, update_day_data_db, read_day_rating, read_week_rating, \
    get_yesterday, get_yesterweek, export_data_to_file, add_new_user
from Config.config_reader import admin, chat_id

from Keyboards.keyboards import make_row_keyboard

router: Router = Router()

available_genders = ["Мужчина", "Женщина"]
available_categories = ["1", "2", "3"]


class Znakomstvo(StatesGroup):
    add_name = State()
    choosing_genders = State()
    choosing_categories = State()


# Обработчик сообщения команды /start
@router.message(F.chat.type == "private", CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    # проверка на наличия в БД данных о пользователе
    if not read_user_statistics_from_db(message.from_user.id):
        await message.answer(f"Привет, <b>{message.from_user.full_name}</b>!\n"
                             f"Давай познакомимся. Напишите свои имя и фамилию:")
        await state.set_state(Znakomstvo.add_name)
    else:
        await message.answer(f"Мы уже познакомились")


@router.message(Znakomstvo.add_name)
async def name_added(message: Message, state: FSMContext):
    await state.update_data(name_added=message.text)
    user_data = await state.get_data()
    await message.answer(
        text=f"Приятно познакомится, {user_data['name_added']}! Теперь укажите свой пол:",
        reply_markup=make_row_keyboard(available_genders, txt='Ваш пол:'))
    await state.set_state(Znakomstvo.choosing_genders)


@router.message(Znakomstvo.choosing_genders, F.text.in_(available_genders))
async def gender_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_gender=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь выберите вашу категорию бега:",
        reply_markup=make_row_keyboard(available_categories, txt='Ваша категория бега:')
    )
    await state.set_state(Znakomstvo.choosing_categories)


@router.message(Znakomstvo.choosing_genders)
async def gender_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого пола.\n\n"
             "Пожалуйста, выберите один из вариантов:",
        reply_markup=make_row_keyboard(available_genders, txt='Ваш пол:')
    )


@router.message(Znakomstvo.choosing_categories, F.text.in_(available_categories))
async def categories_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    telegram_id = message.from_user.id
    username = message.from_user.full_name
    fullname = user_data['name_added']
    gender = user_data['chosen_gender']
    category = message.text.lower()
    await message.answer(
        text=f"Вас зовут: {fullname}.\n"
             f"Вы: {gender}.\n"
             f"Ваша категория: {category}",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
    add_new_user(telegram_id, username, fullname, gender, category)


@router.message(Znakomstvo.choosing_categories)
async def category_incorrectly(message: Message):
    await message.answer(
        text="У нас нет такой категории.\n"
             "Пожалуйста, выберите один из вариантов:",
        reply_markup=make_row_keyboard(available_categories, txt='Ваша категория бега:')
    )


# Обработчик команды добавления новой статистики /д
@router.message(F.chat.type == "supergroup", Command("д"))
async def cmd_add_statistics(
        message: Message,
        command: CommandObject
):
    telegram_id = message.from_user.id
    # Обработка ошибок ввода пробега
    try:
        new_mileage = float(command.args.split()[0])
        new_mileage_time = float(command.args.split()[1])
    # пробег и время число?
    except ValueError:
        await message.reply("Укажите пробег и время числом")
        return
    # пробег и время указаны после команды?
    except TypeError:
        await message.reply("Укажите пробег и время")
        return
    except AttributeError:
        await message.reply("Укажите пробег и время")
        return
    except IndexError:
        await message.reply("Укажите пробег и время")
        return

        # проверка на наличие пользователя в БД
    if not read_user_statistics_from_db(message.from_user.id):
        await message.reply("Для начала, познакомься с ботом: https://t.me/SportStatistics_bot\n")
        return
    # нереальный дневной пробег
    elif len(command.args.split()) > 2:
        await message.reply("Слишком много аргументов")
        return
    elif new_mileage == 0 or new_mileage_time == 0:
        await message.reply("Пробег и время должны быть больше 0")
        return
    elif new_mileage > 300:
        await message.reply("Обманщик!")
        return
    else:
        # добавление пробега в БД
        day_mileage, day_mileage_time = update_day_data_db(telegram_id, new_mileage, new_mileage_time)

        await message.reply(
            f"Новый пробег зафиксирован\n"
            f"Итого за сегодня: {round(day_mileage, 2)} км. за {day_mileage_time} мин."
        )



# обработчика команды /помощь
@router.message(F.chat.type == "supergroup", Command("помощь"))
async def cmd_help(
        message: Message,
):
    await message.reply(
        f"Для работы с ботом нажми https://t.me/SportStatistics_bot\n"
        f"Добавление пробега:\n"
        f"/д км.км мин\n"
        f"Уменьшение пробега:\n"
        f"/д -км.км -мин\n"
        f"Личная статистика:\n"
        f"/стат"
    )


# обработчика команды /стат
@router.message(Command("statistics"))
async def cmd_user_statistics(
        message: Message,
        bot: Bot
):
    telegram_id = message.from_user.id
    user_statistics = read_user_statistics_from_db(telegram_id)

    if user_statistics:
        username, fullname, gender, category, day_mileage, day_mileage_time, week_mileage, week_mileage_time, \
            month_mileage, month_mileage_time, total_mileage, total_mileage_time = user_statistics

        await bot.send_message(
            telegram_id,
            f"Твоя статистика бега за {datetime.now().strftime('%d.%m.%Y')}:\n"
            f"\n"
            f"Дневной пробег: <b>{round(day_mileage, 2)}</b> км. за <b>{day_mileage_time}</b> мин.\n"
            f"Недельный пробег: <b>{round(week_mileage, 2)}</b> км. за <b>{week_mileage_time}</b> мин.\n"
            f"Месячный пробег: <b>{round(month_mileage, 2)}</b> км. за <b>{month_mileage_time}</b> мин.\n"
            f"Общий пробег: <b>{round(total_mileage, 2)}</b> км. за <b>{total_mileage_time}</b> мин."
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
        razdelitel = ""
        yesterday = get_yesterday()
        user_sum = len(day_rating)

        for (index, i) in enumerate(day_rating):
            float_day_rating = round(float(str(day_rating[index][2]).replace(',', '.')), 2)
            summ_mileage += float_day_rating
            if index <= 4:
                winners += f"{index + 1}. {day_rating[index][1]} - {float_day_rating} км.\n"
            elif index >= user_sum - 3:
                razdelitel = f"...\n"
                loosers += f"{index + 1}. {day_rating[index][1]} - {float_day_rating} км.\n"
        text_answer = f"{winners}" \
                      f"{razdelitel}" \
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
                razdelitel = f"...\n"
                loosers += f"{index + 1}. {week_rating[index][1]} - {float_week_rating} км.\n"
        text_answer = f"{winners}" \
                      f"{razdelitel}" \
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


@router.message(F.new_chat_members)
async def chat_new_user_added(message: Message):
    for user in message.new_chat_members:
        content = Text(
            "Привет, ", Bold(user.full_name), ".\n"
                                              "Для начала, познакомься с ботом: https://t.me/SportStatistics_bot\n"
                                              "Справка по боту: /помощь"
        )
        await message.reply(
            **content.as_kwargs()
        )
