import asyncio
import logging
import os
import datetime
from aiogram import Router, F, Bot, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.formatting import Text, Bold
from Handlers.db_handler import (
    read_user_statistics_from_db, update_day_data_db, read_day_rating, read_week_rating, get_yesterday, get_yesterweek,
    export_data_to_file, add_new_user, read_day_time_rating, update_today_data_db, read_day_points_rating,
    read_week_time_rating, read_week_points_rating, read_club_rating, update_bid, read_user_bids_from_db)
from Config.config_reader import admin, chat_id

from Keyboards.keyboards import make_row_keyboard, get_start_keyboard, get_cancel_keyboard, get_donate_button

# from Keyboards.inline_keyboard import get_inline_kb

router: Router = Router()

available_genders = ["️Парень", "Девушка"]
available_categories = ["Begym", "Совкомбанк", "Казбек", "Эльбрус", "ДомРФ", "КРОК"]

is_delete_mileage = False


async def reset_fsm_state(user_id, state, timeout=3):
    last_message_time = state.get('last_message_time')
    if last_message_time is None:
        # First message, save the time
        state['last_message_time'] = asyncio.get_running_loop().time()
        return

    current_time = asyncio.get_running_loop().time()
    time_since_last_message = current_time - last_message_time
    if time_since_last_message > timeout:
        # User has not written a new message within 5 minutes, reset the state
        state.reset_state()
        state['last_message_time'] = current_time


class Znakomstvo(StatesGroup):
    add_name = State()
    choosing_genders = State()
    choosing_categories = State()


class Mileage_add_status(StatesGroup):
    add_mileage_km = State()
    add_mileage_time_hours = State()
    add_mileage_time_minutes = State()
    add_mileage_time_seconds = State()


class Bids(StatesGroup):
    choosing_bid_category_man = State()
    add_bid_category_man = State()
    choosing_bid_category_woman = State()
    add_bid_category_woman = State()


def convert_seconds(seconds):
    return str(datetime.timedelta(seconds=seconds))


# Обработчик сообщения команды /start
@router.message(CommandStart())
async def command_start_handler(message: Message, bot: Bot) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Привет, <b>{message.from_user.full_name}</b>!\nВыбери действие:",
                           reply_markup=get_start_keyboard(),
                           # reply_markup=get_inline_kb()
                           )


@router.message(F.chat.type == "private", F.text == "✅ Регистрация")
async def znakomstvo(message: Message, state: FSMContext) -> None:
    # проверка на наличия в БД данных о пользователе
    if not read_user_statistics_from_db(message.from_user.id):
        await message.answer(f"Привет, <b>{message.from_user.full_name}</b>!\n"
                             f"Напишите свои имя и фамилию:",
                             reply_markup=get_cancel_keyboard(txt='Имя Фамилия'))
        await state.set_state(Znakomstvo.add_name)
    else:
        await message.answer(f"Вы уже зарегистрировались", reply_markup=get_start_keyboard())


@router.message(Znakomstvo.add_name, F.text != "❌ Отмена")
async def name_added(message: Message, state: FSMContext):
    # if len(message.text) > 50:
    #     await message.answer(f"Имя и фамилия не могут быть длиннее 50 символов")
    #     return
    await state.update_data(name_added=message.text)
    user_data = await state.get_data()
    await message.answer(
        text=f"Приятно познакомится, {user_data['name_added']}! Теперь укажите кто Вы:",
        reply_markup=make_row_keyboard(available_genders, txt='Вы:'))
    await state.set_state(Znakomstvo.choosing_genders)


@router.message(Znakomstvo.choosing_genders, F.text.in_(available_genders))
async def gender_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_gender=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь выберите ваш клуб:",
        reply_markup=make_row_keyboard(available_categories, txt='Ваш клуб:')
    )
    await state.set_state(Znakomstvo.choosing_categories)


@router.message(Znakomstvo.choosing_genders, F.text != "❌ Отмена")
async def gender_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого пола.\n"
             "Пожалуйста, выберите один из вариантов:",
        reply_markup=make_row_keyboard(available_genders, txt='Вы:')
    )


@router.message(Znakomstvo.choosing_categories, F.text.in_(available_categories))
async def categories_chosen(message: Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    telegram_id = message.from_user.id
    username = message.from_user.full_name
    fullname = user_data['name_added']
    gender = user_data['chosen_gender']
    category = message.text
    gender_hi = "новый участник! 🏃🏻‍♂️"
    if gender == available_genders[1].lower():
        gender_hi = "новая участница! 🏃🏻‍♀️"
    await message.answer(
        text=f"Спасибо за регистрацию!\n"
             f"Вас зовут: {fullname}.\n"
             f"Вы: {gender}.\n"
             f"Ваш клуб: {category}",
        reply_markup=get_start_keyboard()
    )
    await state.clear()
    add_new_user(telegram_id, username, fullname, gender, category)

    await bot.send_message(
        chat_id,
        f"У нас {gender_hi}\n"
        f"<b>{fullname}</b> из клуба {category}\n"
        f"Желаем успехов в челлендже!"
    )


@router.message(Znakomstvo.choosing_categories, F.text != "❌ Отмена")
async def category_incorrectly(message: Message):
    await message.answer(
        text="У нас нет такого клуба.\n"
             "Пожалуйста, выберите один из вариантов:",
        reply_markup=make_row_keyboard(available_categories, txt='Ваш клуб:')
    )


@router.message(F.chat.type == "private", F.text == "🏆 Ставка")
async def add_bid(message: Message, state: FSMContext):
    # проверка на регистрацию в челлендже
    # проверка на наличия в БД данных о ставке
    # bids = read_user_statistics_from_db(message.from_user.id)
    bids = read_user_bids_from_db(message.from_user.id)
    bids_on = False
    if not bids:
        await message.answer(f"Привет, <b>{message.from_user.full_name}</b>!\n"
                             f"Для начала, зарегистрируйся.",
                             reply_markup=get_start_keyboard())
    else:
        if bids[4]:
            await message.answer(f"Вы уже сделали ставку:\n"
                                 f"{bids[5]} км. на парней из клуба {bids[4]}\n"
                                 f"{bids[7]} км. на девушек из клуба {bids[6]}",
                                 reply_markup=get_start_keyboard())

        elif bids_on:
            await message.answer(f"Привет, <b>{bids[1]}</b>!\n"
                                 f"Здесь ты можешь поставить свои километры пробега на то, какой клуб "
                                 f"парней и девушек выиграет.\n"
                                 f"Если ты угадаешь, то ставка прибавится к твоему итоговому пробегу.\n"
                                 f"Если нет, ставка вычтется из твоего итогового пробега.\n"
                                 f"Максимальная суммарная ставка на клубы 35 км.\n"
                                 f"Готов рискнуть? Тогда сначала выбери клуб парней:",
                                 reply_markup=make_row_keyboard(available_categories, txt='Выбери мужской клуб.'))
            await state.set_state(Bids.choosing_bid_category_man)
        else:
            await message.answer(f"Прием ставок окончен.",
                                 reply_markup=get_start_keyboard())


@router.message(Bids.choosing_bid_category_man, F.chat.type == "private", F.text.in_(available_categories),
                F.text != "❌ Отмена")
async def bid_man_category_chosen(message: Message, state: FSMContext):
    await state.update_data(bid_man_category=message.text)
    await message.answer(
        text="Отлично! Укажи сколько километров готов(а) поставить на мужской клуб.",
        reply_markup=get_cancel_keyboard(txt="Ставка, км.км")
    )
    await state.set_state(Bids.add_bid_category_man)


@router.message(Bids.add_bid_category_man, F.chat.type == "private", F.text != "❌ Отмена")
async def bid_man_added(message: Message, state: FSMContext):
    try:
        if float(message.text) == 0 or float(message.text) < 0 or float(message.text) > 35:
            raise ValueError()
        await state.update_data(bid_man=float(message.text))
        await message.answer(
            text="Отлично! Теперь выбери женский клуб.",
            reply_markup=make_row_keyboard(available_categories, txt='Выбери женский клуб.'))
        await state.set_state(Bids.choosing_bid_category_woman)
    except ValueError:
        await message.answer(text="Принимаются ставки суммарно не более 35 км.",
                             reply_markup=get_cancel_keyboard(txt="Введите расстояние в км.км"))


@router.message(Bids.choosing_bid_category_woman, F.chat.type == "private",
                F.text.in_(available_categories), F.text != "❌ Отмена")
async def bid_woman_category_chosen(message: Message, state: FSMContext):
    await state.update_data(bid_woman_category=message.text)
    await message.answer(
        text="Отлично! Укажи сколько километров готов(а) поставить на женский клуб.",
        reply_markup=get_cancel_keyboard(txt="Ставка, км.км")
    )
    await state.set_state(Bids.add_bid_category_woman)


@router.message(Bids.add_bid_category_woman, F.chat.type == "private", F.text != "❌ Отмена")
async def bid_man_added(message: Message, bot: Bot, state: FSMContext):
    try:
        user_data = await state.get_data()
        if float(message.text) == 0 or float(message.text) < 0 or float(message.text) > 35 - user_data['bid_man']:
            raise ValueError()
        await state.update_data(bid_woman=float(message.text))
        user_data = await state.get_data()
        telegram_id = message.from_user.id
        bid_man_category = user_data['bid_man_category']
        bid_man = user_data['bid_man']
        bid_woman_category = user_data['bid_woman_category']
        bid_woman = user_data['bid_woman']
        await message.answer(
            text=f"Вы сделали ставку:\n"
                 f"{bid_man} км. на парней из клуба {bid_man_category}\n"
                 f"{bid_woman} км. на девушек из клуба {bid_woman_category}\n"
                 f"Желаем удачи!",
            reply_markup=get_start_keyboard())
        await state.clear()
        update_bid(telegram_id, bid_man_category, bid_man, bid_woman_category, bid_woman)
        await bot.send_message(
            chat_id,
            f"<b>{message.from_user.full_name}</b> сделал ставку!\n"
        )
    except ValueError:
        await message.answer(text="Принимаются ставки суммарно не более 35 км.",
                             reply_markup=get_cancel_keyboard(txt="Введите расстояние в км.км"))


@router.message(Bids.choosing_bid_category_man, F.text != "❌ Отмена")
@router.message(Bids.choosing_bid_category_woman, F.text != "❌ Отмена")
async def bid_category_incorrectly(message: Message):
    await message.answer(
        text="У нас нет такого клуба.\n"
             "Пожалуйста, выберите один из вариантов:",
        reply_markup=make_row_keyboard(available_categories, txt='Выберите клуб:')
    )


@router.message(F.text == "📈 Добавление пробега")
@router.message(F.text == "📉 Удаление пробега")
@router.message(F.chat.type == "private", Command("add"))
async def command_add(message: Message, state: FSMContext) -> None:
    # проверка на наличия в БД данных о пользователе
    if not read_user_statistics_from_db(message.from_user.id):
        await message.answer(f"Привет, <b>{message.from_user.full_name}</b>!\n"
                             f"Для начала необходимо зарегистрироваться.\n",
                             reply_markup=get_start_keyboard()
                             )
        await state.clear()
    else:
        global is_delete_mileage
        if message.text == "📉 Удаление пробега":
            is_delete_mileage = True
        else:
            is_delete_mileage = False
        await message.answer(text="Введите пробег в км",
                             reply_markup=get_cancel_keyboard(txt="Введите пробег в км"),
                             )
        await state.set_state(Mileage_add_status.add_mileage_km)


@router.message(Mileage_add_status.add_mileage_km, F.chat.type == "private", F.text != "❌ Отмена")
async def mileage_km_added(message: Message, state: FSMContext):
    try:
        if float(message.text) == 0 or float(message.text) < 0:
            raise ValueError()
        await state.update_data(mileage_km=float(message.text))
        await message.answer(
            text="Введите часы пробежки:",
            reply_markup=get_cancel_keyboard(txt="Часы пробежки")
        )
        await state.set_state(Mileage_add_status.add_mileage_time_hours)

    except ValueError:
        await message.answer(text="Введите корректный пробег: км.км",
                             reply_markup=get_cancel_keyboard(txt="Введите расстояние в км.км"))


@router.message(Mileage_add_status.add_mileage_time_hours, F.chat.type == "private", F.text != "❌ Отмена")
async def mileage_hour_added(message: Message, state: FSMContext):
    try:
        if int(message.text) > 24 or int(message.text) < 0:
            raise ValueError()
        await state.update_data(mileage_hour=int(message.text))
        await message.answer(
            text="Введите минуты пробежки:",
            reply_markup=get_cancel_keyboard(txt="Введите минуты пробежки")
        )
        await state.set_state(Mileage_add_status.add_mileage_time_minutes)

    except ValueError:
        await message.answer(text="Введи корректное время",
                             reply_markup=get_cancel_keyboard(txt="Введите минуты пробежки"))


@router.message(Mileage_add_status.add_mileage_time_minutes, F.chat.type == "private", F.text != "❌ Отмена")
async def mileage_minutes_added(message: Message, state: FSMContext):
    try:
        if int(message.text) > 60:
            raise ValueError()
        await state.update_data(mileage_minutes=int(message.text))
        await message.answer(
            text="Введите секунды пробежки:",
            reply_markup=get_cancel_keyboard(txt="Введите секунды пробежки")
        )
        await state.set_state(Mileage_add_status.add_mileage_time_seconds)

    except ValueError:
        await message.answer(text="Введи корректное время",
                             reply_markup=get_cancel_keyboard(txt="Введите секунды пробежки"))


# Ввод секунд пробежки, добавление пробежки в БД и ответ в личку и группу
@router.message(Mileage_add_status.add_mileage_time_seconds, F.chat.type == "private", F.text != "❌ Отмена")
async def mileage_seconds_added(message: Message, bot: Bot, state: FSMContext):
    try:
        if int(message.text) > 60:
            raise ValueError()
        await state.update_data(mileage_seconds=int(message.text))
        user_mileage_data = await state.get_data()
        mileage_km = user_mileage_data['mileage_km']
        mileage_hour = user_mileage_data['mileage_hour']
        mileage_minutes = user_mileage_data['mileage_minutes']
        mileage_seconds = user_mileage_data['mileage_seconds']
        full_time_seconds = int(mileage_hour) * 3600 + int(mileage_minutes) * 60 + int(mileage_seconds)
        if ((full_time_seconds / 60) / mileage_km) < 2:
            await message.answer(f"У нас новый мировой рекорд! Или нет?\n"
                                 f"Темп не может быть выше 2 мин./км.")
            await message.answer(text="Введите пробег в км",
                                 reply_markup=get_cancel_keyboard(txt="Введите пробег в км"),
                                 )
            await state.set_state(Mileage_add_status.add_mileage_km)
            return
        telegram_id = message.from_user.id

        global is_delete_mileage

        # добавление пробега
        if not is_delete_mileage:
            new_mileage_points = update_today_data_db(telegram_id, mileage_km, full_time_seconds)
            day_mileage, day_mileage_time_seconds, day_mileage_points = update_day_data_db(telegram_id, mileage_km,
                                                                                           full_time_seconds,
                                                                                           new_mileage_points)
            new_mileage_time = convert_seconds(full_time_seconds)
            day_mileage_time = convert_seconds(day_mileage_time_seconds)
            await bot.send_message(telegram_id,
                                   f"Новый пробег зафиксирован:\n"
                                   f"<b>{round(mileage_km, 2)}</b> км. за <b>{new_mileage_time}</b>. "
                                   f"Баллы: <b>{round(new_mileage_points, 2)}</b>\n"
                                   f"Итого за сегодня:\n"
                                   f"<b>{round(day_mileage, 2)}</b> км. за <b>{day_mileage_time}</b>. "
                                   f"Баллы: <b>{round(day_mileage_points, 2)}</b>",
                                   reply_markup=get_start_keyboard()
                                   )
            await state.clear()
            await bot.send_message(
                chat_id,
                f"<b>{message.from_user.full_name}</b> добавил пробег:\n"
                f"{round(mileage_km, 2)} км. за {new_mileage_time}. Баллы: {round(new_mileage_points, 2)}\n"
            )
        # удаление пробега
        else:
            new_mileage_points = update_today_data_db(telegram_id, -mileage_km, -full_time_seconds)
            day_mileage, day_mileage_time_seconds, day_mileage_points = update_day_data_db(telegram_id, -mileage_km,
                                                                                           -full_time_seconds,
                                                                                           new_mileage_points)
            new_mileage_time = convert_seconds(full_time_seconds)
            day_mileage_time = convert_seconds(day_mileage_time_seconds)
            await bot.send_message(telegram_id,
                                   f"Удалён пробег:\n"
                                   f"<b>{round(mileage_km, 2)}</b> км. за <b>{new_mileage_time}</b>. "
                                   f"Баллы: <b>{round(new_mileage_points, 2)}</b>\n"
                                   f"Итого за сегодня:\n"
                                   f"<b>{round(day_mileage, 2)}</b> км. за <b>{day_mileage_time}</b>. "
                                   f"Баллы: <b>{round(day_mileage_points, 2)}</b>",
                                   reply_markup=get_start_keyboard()
                                   )
            await state.clear()
            await bot.send_message(
                chat_id,
                f"<b>{message.from_user.full_name}</b> удалил пробег:\n"
                f"{round(mileage_km, 2)} км. за {new_mileage_time}. Баллы: {round(new_mileage_points, 2)}\n"
            )

    except ValueError:
        await message.answer(text="Введи корректное время",
                             reply_markup=get_cancel_keyboard())


# обработка нажатия кнопки Отмена
@router.message(F.chat.type == "private", F.text == "❌ Отмена")
async def cancel_button(message: Message, state: FSMContext):
    await message.answer(
        text=f"Действие отменено",
        reply_markup=get_start_keyboard()
        # reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


# Обработчик команды добавления новой статистики /д
# @router.message(F.chat.type == "private", Command("д"))
# async def cmd_add_statistics(message: Message, bot: Bot, command: CommandObject):
#     telegram_id = message.from_user.id
#     # Обработка ошибок ввода пробега
#     try:
#         new_mileage = float(command.args.split()[0])
#         new_mileage_time = command.args.split()[1]
#         print(f'Время пробега: {new_mileage_time}')
#         # пробег и время число?
#     except ValueError:
#         await message.reply("Укажите пробег и время числом")
#         return
#     # пробег и время указаны после команды?
#     except TypeError:
#         await message.reply("Укажите пробег и время")
#         return
#     except AttributeError:
#         await message.reply("Укажите пробег и время")
#         return
#     except IndexError:
#         await message.reply("Укажите пробег и время")
#         return
#         # проверка на наличие пользователя в БД
#     if not read_user_statistics_from_db(message.from_user.id):
#         await message.reply(f"Для начала, зарегистрируйся: {botname}\n")
#         return
#     # нереальный дневной пробег
#     elif len(command.args.split()) > 2:
#         await message.reply("Слишком много аргументов")
#         return
#     elif len(new_mileage_time) != 8:
#         await message.reply("Неверный формат времени. Формат времени: ЧЧ:ММ:СС")
#         return
#     elif new_mileage == 0:
#         await message.reply("Пробег и время должны быть больше 0")
#         return
#     elif new_mileage > 300:
#         await message.reply("Обманщик!")
#         return
#
#     else:
#         # перевод времени в секунды
#         new_mileage_time_seconds = int(new_mileage_time[:2]) * 3600 + int(new_mileage_time[3:5]) * 60 + int(
#             new_mileage_time[6:])
#         print(f'Время пробега в секундах: {new_mileage_time_seconds}')
#         print(f'Темп: {(new_mileage_time_seconds / 60) / new_mileage}')
#         if ((new_mileage_time_seconds / 60) / new_mileage) < 2:
#             await message.reply(f"У нас новый мировой рекорд! Или нет?\n"
#                                 f"Темп не может быть выше 2 мин./км.")
#             return
#         new_mileage_points = update_today_data_db(telegram_id, new_mileage, new_mileage_time_seconds)
#         day_mileage, day_mileage_time_seconds, day_mileage_points = update_day_data_db(telegram_id, new_mileage,
#                                                                                        new_mileage_time_seconds,
#                                                                                        new_mileage_points)
#         day_mileage_time = convert_seconds(day_mileage_time_seconds)
#
#         await message.reply(
#             f"Новый пробег зафиксирован:\n"
#             f"{round(new_mileage, 2)} км. за {new_mileage_time}. Баллы: {round(new_mileage_points, 2)}\n"
#             f"Итого за сегодня:\n"
#             f"{round(day_mileage, 2)} км. за {day_mileage_time}. Баллы: {round(day_mileage_points, 2)}"
#         )
#         await bot.send_message(
#             chat_id,
#             f"{message.from_user.full_name} добавил пробег:\n"
#             f"{round(new_mileage, 2)} км. за {new_mileage_time}. Баллы: {round(new_mileage_points, 2)}")


# обработчика команды /помощь
@router.message(F.text == "ℹ️ Дополнительная информация")
@router.message(F.chat.type == "private", Command("help"))
async def cmd_help(message: Message, bot: Bot):
    donate_button = InlineKeyboardButton(text="💸 Поддержать проект", url="https://pay.cloudtips.ru/p/cbd68797")
    message_button = InlineKeyboardButton(text="🆘 Обратная связь", url="https://t.me/AVSolovyov")
    row = [donate_button]
    rows = [[donate_button], [message_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    await bot.send_message(message.from_user.id,
                           f"Понравился бот? Поддержите нас",
                           reply_markup=markup
                           # reply_markup=get_donate_button()
                           )


# обработчика команды /стат
@router.message(F.text == "📝 Личная статистика")
@router.message(F.chat.type == "private", Command("statistics"))
async def cmd_user_statistics(message: Message, bot: Bot):
    telegram_id = message.from_user.id
    user_statistics = read_user_statistics_from_db(telegram_id)
    if user_statistics:
        username, fullname, gender, category, day_mileage, day_mileage_time_seconds, day_mileage_points, week_mileage, \
            week_mileage_time_seconds, week_mileage_points, month_mileage, month_mileage_time_seconds, \
            month_mileage_points, total_mileage, total_mileage_time_seconds, total_mileage_points = user_statistics

        day_mileage_time = convert_seconds(user_statistics[5])
        week_mileage_time = convert_seconds(user_statistics[8])
        # month_mileage_time = convert_seconds(user_statistics[11])
        total_mileage_time = convert_seconds(user_statistics[14])

        await bot.send_message(
            telegram_id,
            f"Твоя статистика бега за {datetime.datetime.now().strftime('%d.%m.%Y')}:\n"
            f"\n"
            f"Дневной пробег: <b>{round(day_mileage, 2)}</b> км. за <b>{day_mileage_time}</b>, "
            f"<b>{round(day_mileage_points, 2)}</b> баллов\n"
            f"Недельный пробег: <b>{round(week_mileage, 2)}</b> км. за <b>{week_mileage_time}</b>, "
            f"<b>{round(week_mileage_points, 2)}</b> баллов\n"
            # f"Месячный пробег: <b>{round(month_mileage, 2)}</b> км. за <b>{month_mileage_time}</b>, "
            # f"<b>{round(month_mileage_points, 2)}</b> баллов\n"
            f"Общий пробег: <b>{round(total_mileage, 2)}</b> км. за <b>{total_mileage_time}</b>, "
            f"<b>{round(total_mileage_points, 2)}</b> баллов",
            reply_markup=get_start_keyboard()
        )
    else:
        await bot.send_message(
            telegram_id,
            f"Для начала необходимо зарегистрироваться.",
            reply_markup=get_start_keyboard()
        )


async def show_club_mileage_rating(bot: Bot):
    '''
    Функция выводит накопительный рейтинг клуба за все предыдущие дни.
    Рейтинг делится на М и Ж.
    Суммируется максимальный пробег у всех человек в клубе.
    Кол-во человек в клубе ограничивается минимальный кол-м в любом клубе.
    :param bot:
    :return:
    '''
    yesterday = get_yesterday()
    try:
        man_rating, woman_rating = read_club_rating()
        rating_man = ""
        for (index, i) in enumerate(man_rating):
            float_club_rating = round(float(str(man_rating[index][1]).replace(',', '.')), 2)
            rating_man += f"{index + 1}. {man_rating[index][0]} - {float_club_rating} км.\n"
        text_answer_man = f"{rating_man}"

        rating_woman = ""
        for (index, i) in enumerate(woman_rating):
            float_club_rating = round(float(str(woman_rating[index][1]).replace(',', '.')), 2)
            rating_woman += f"{index + 1}. {woman_rating[index][0]} - {float_club_rating} км.\n"
        text_answer_woman = f"{rating_woman}"
    except IndexError:
        await bot.send_message(chat_id, f'Нет пробега за {yesterday}')
    await bot.send_message(
        chat_id,
        f"#Итог_на {yesterday}\n"
        f"#Рейтинг_парни:"
        f"\n"
        f"{text_answer_man}"
    )
    await bot.send_message(
        chat_id,
        f"#Итог_на {yesterday}\n"
        f"#Рейтинг_девушки:"
        f"\n"
        f"{text_answer_woman}"
    )


# отправка дневного рейтинга в общий чат
async def show_day_mileage_rating(bot: Bot):
    try:
        day_rating = read_day_rating()
        summ_mileage = 0
        winners = ""
        loosers = ""
        delimiter = ""
        yesterday = get_yesterday()
        for (index, i) in enumerate(day_rating):
            float_day_rating = round(float(str(day_rating[index][3]).replace(',', '.')), 2)
            summ_mileage += float_day_rating
            if index <= 4:
                winners += f"{index + 1}. {day_rating[index][2]}. {day_rating[index][1]} - {float_day_rating} км.\n"
            elif index >= len(day_rating) - 3:
                delimiter = f"...\n"
                loosers += f"{index + 1}. {day_rating[index][2]}. {day_rating[index][1]} - {float_day_rating} км.\n"
        text_answer = f"{winners}{delimiter}{loosers}"
    except IndexError:
        await bot.send_message(chat_id, f'Нет пробега за {yesterday}')
    await bot.send_message(
        chat_id,
        f"#Итог_дня {yesterday}\n"
        f"#Общий_пробег: {round(summ_mileage, 2)}км.\n"
        f"\n"
        f"{text_answer}"
    )


async def show_day_time_rating(bot: Bot):
    try:
        day_rating = read_day_time_rating()
        summ_mileage = 0
        winners = ""
        loosers = ""
        delimiter = ""
        yesterday = get_yesterday()

        for (index, i) in enumerate(day_rating):
            day_time_rating_seconds = day_rating[index][2]
            summ_mileage += day_time_rating_seconds
            if index <= 4:
                winners += f"{index + 1}. {day_rating[index][1]} - {convert_seconds(day_time_rating_seconds)}\n"
            elif index >= len(day_rating) - 3:
                delimiter = f"...\n"
                loosers += f"{index + 1}. {day_rating[index][1]} - {convert_seconds(day_time_rating_seconds)}\n"

        text_answer = f"{winners}" \
                      f"{delimiter}" \
                      f"{loosers}"
    except IndexError:
        await bot.send_message(chat_id, f'Нет пробега за {yesterday}')

    await bot.send_message(
        chat_id,
        f"#Итог_дня {yesterday}\n"
        f"#Командное_время: {convert_seconds(summ_mileage)}\n"
        f"\n"
        f"{text_answer}"
    )


async def show_day_points_rating(bot: Bot):
    try:
        day_rating = read_day_points_rating()
        summ_mileage = 0
        winners = ""
        loosers = ""
        delimiter = ""
        yesterday = get_yesterday()

        for (index, i) in enumerate(day_rating):
            float_day_rating = round(float(str(day_rating[index][2]).replace(',', '.')), 2)
            summ_mileage += float_day_rating
            if index <= 4:
                winners += f"{index + 1}. {day_rating[index][1]} - {float_day_rating}\n"
            elif index >= len(day_rating) - 3:
                delimiter = f"...\n"
                loosers += f"{index + 1}. {day_rating[index][1]} - {float_day_rating}\n"

        text_answer = f"{winners}" \
                      f"{delimiter}" \
                      f"{loosers}"
    except IndexError:
        await bot.send_message(chat_id, f'Нет пробега за {yesterday}')

    await bot.send_message(
        chat_id,
        f"#Итог_дня {yesterday}\n"
        f"#Командные_баллы: {round(summ_mileage, 2)}\n"
        f"\n"
        f"{text_answer}"
    )


async def show_week_mileage_rating(bot: Bot):
    try:
        week_rating = read_week_rating()
        text_answer = ""
        summ_mileage = 0
        winners = ""
        loosers = ""
        delimiter = ""
        yesterweek = get_yesterweek()
        user_sum = len(week_rating)

        for (index, i) in enumerate(week_rating):
            float_week_rating = round(float(str(week_rating[index][3]).replace(',', '.')), 2)
            summ_mileage += float_week_rating
            if index <= 4:
                winners += f"{index + 1}.{week_rating[index][2]}. {week_rating[index][1]} - {float_week_rating} км.\n"
            elif index >= user_sum - 3:
                delimiter = f"...\n"
                loosers += f"{index + 1}.{week_rating[index][2]}. {week_rating[index][1]} - {float_week_rating} км.\n"
        text_answer = f"{winners}" \
                      f"{delimiter}" \
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


async def show_week_time_rating(bot: Bot):
    try:
        week_rating = read_week_time_rating()
        summ_mileage = 0
        winners = ""
        loosers = ""
        delimiter = ""
        yesterweek = get_yesterweek()

        for (index, i) in enumerate(week_rating):
            week_rating_seconds = week_rating[index][2]
            summ_mileage += week_rating_seconds
            if index <= 4:
                winners += f"{index + 1}. {week_rating[index][1]} - {convert_seconds(week_rating_seconds)}\n"
            elif index >= len(week_rating) - 3:
                delimiter = f"...\n"
                loosers += f"{index + 1}. {week_rating[index][1]} - {convert_seconds(week_rating_seconds)}\n"

        text_answer = f"{winners}" \
                      f"{delimiter}" \
                      f"{loosers}"
    except IndexError:
        text_answer = f'Нет пробега за {yesterweek} неделю'

    await bot.send_message(
        chat_id,
        f"#Рейтинг_недели {yesterweek}\n"
        f"#Командное_время: {convert_seconds(summ_mileage)}\n"
        f"\n"
        f"{text_answer}"
    )


async def show_week_points_rating(bot: Bot):
    try:
        week_rating = read_week_points_rating()
        summ_mileage = 0
        winners = ""
        loosers = ""
        delimiter = ""
        yesterweek = get_yesterweek()

        for (index, i) in enumerate(week_rating):
            float_week_rating = round(float(str(week_rating[index][2]).replace(',', '.')), 2)
            summ_mileage += float_week_rating
            if index <= 4:
                winners += f"{index + 1}. {week_rating[index][1]} - {float_week_rating}\n"
            elif index >= len(week_rating) - 3:
                delimiter = f"...\n"
                loosers += f"{index + 1}. {week_rating[index][1]} - {float_week_rating}\n"

        text_answer = f"{winners}" \
                      f"{delimiter}" \
                      f"{loosers}"
    except IndexError:
        text_answer = f'Нет пробега за {yesterweek} неделю'

    await bot.send_message(
        chat_id,
        f"#Рейтинг_недели {yesterweek}\n"
        f"#Командные_баллы: {round(summ_mileage, 2)}\n"
        f"\n"
        f"{text_answer}"
    )


# Отправка дневного рейтинга ботом
async def show_day_rating(bot: Bot):
    await show_day_mileage_rating(bot)
    # await show_day_time_rating(bot)
    # await show_day_points_rating(bot)


# Отправка дневного рейтинга по команде /day
@router.message(F.chat.type == "private", Command("day"))
async def cmd_day_rating(message: Message, bot: Bot):
    if message.from_user.id in admin:
        await show_day_mileage_rating(bot)
        await show_club_mileage_rating(bot)
        # await show_day_time_rating(bot)
        # await show_day_points_rating(bot)


# Отправка недельного рейтинга ботом
async def show_week_rating(bot: Bot):
    await show_week_mileage_rating(bot)
    # await show_week_time_rating(bot)
    # await show_week_points_rating(bot)


# Отправка дневного рейтинга по команде /week
@router.message(F.chat.type == "private", Command("week"))
async def cmd_week_rating(message: Message, bot: Bot):
    if message.from_user.id in admin:
        await show_week_mileage_rating(bot)
        # await show_week_time_rating(bot)
        # await show_week_points_rating(bot)


@router.message(F.chat.type == "private", Command("файл"))
async def cmd_export_data_to_file(message: types.Document, bot: Bot):
    if message.from_user.id in admin:
        filename = export_data_to_file()

        file_to_send = FSInputFile(filename)

        if os.path.exists(filename):
            await bot.send_document(message.from_user.id, file_to_send, reply_markup=get_start_keyboard())
            os.remove(filename)
        else:
            await bot.send_message(message.from_user.id, "Файл не найден. Проверьте путь к файлу.",
                                   reply_markup=get_start_keyboard())
    else:
        await message.answer(f"Эта команда для админа!", reply_markup=get_start_keyboard())


@router.message(F.new_chat_members)
async def chat_new_user_added(message: Message):
    bot_button = InlineKeyboardButton(text="Регистрация в челлендже", url="https://t.me/SportStatistics_bot")
    row = [bot_button]
    rows = [row]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    for user in message.new_chat_members:
        content = Text(
            "Привет, ", Bold(user.full_name), "! Для участия в челлендже, зарегистрируйся"
        )
        await message.reply(
            **content.as_kwargs(),
            reply_markup=markup,
        )
