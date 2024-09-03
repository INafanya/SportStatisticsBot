from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram import types


def get_start_keyboard(txt='Выберите действие'):
    button_1 = KeyboardButton(text="✅ Регистрация")
    button_2 = KeyboardButton(text="📈 Добавление пробега")
    button_3 = KeyboardButton(text="📉 Удаление пробега")
    button_4 = KeyboardButton(text="📝 Личная статистика")
    button_5 = KeyboardButton(text="ℹ️ Дополнительная информация")
    button_6 = KeyboardButton(text="🏆 Ставка")
    markup = ReplyKeyboardMarkup(
        keyboard=[[button_1, button_6], [button_2, button_3], [button_4], [button_5]],
        resize_keyboard=True,
        input_field_placeholder=txt
        # one_time_keyboard=True,
    )
    return markup


def get_numbers_keyboard():
    n_1 = KeyboardButton(text="1")
    n_2 = KeyboardButton(text="2")
    n_3 = KeyboardButton(text="3")
    n_4 = KeyboardButton(text="4")
    n_5 = KeyboardButton(text="5")
    n_6 = KeyboardButton(text="6")
    n_7 = KeyboardButton(text="7")
    n_8 = KeyboardButton(text="8")
    n_9 = KeyboardButton(text="9")
    n_10 = KeyboardButton(text="0")
    n_11 = KeyboardButton(text=",")
    n_12 = KeyboardButton(text="Ввод")
    n_13 = KeyboardButton(text="Назад")
    n_14 = KeyboardButton(text="Выход")
    row_1 = [n_1, n_2, n_3]
    row_2 = [n_4, n_5, n_6]
    row_3 = [n_7, n_8, n_9]
    row_4 = [n_10, n_11, n_12]
    row_5 = [n_13, n_14]
    markup = ReplyKeyboardMarkup(
        keyboard=[row_1, row_2, row_3, row_4, row_5],
        resize_keyboard=True
    )
    return markup


def get_yes_no_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да")], [KeyboardButton(text="Нет")]],
        resize_keyboard=True,
    )
    return markup


def get_cancel_keyboard(txt=''):
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        input_field_placeholder=txt
    )
    return markup


def make_row_keyboard(items: list[str], txt='') -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param txt: текст в поле ввода
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    if len(items) < 3:
        row = [KeyboardButton(text=item) for item in items]
        row_cancel = [KeyboardButton(text="❌ Отмена")]
        return ReplyKeyboardMarkup(
            keyboard=[row, row_cancel],
            resize_keyboard=True,
            input_field_placeholder=txt
        )
    else:
        row_1 = [KeyboardButton(text=item) for item in items[:3]]
        row_2 = [KeyboardButton(text=item) for item in items[3:]]
        row_cancel = [KeyboardButton(text="❌ Отмена")]
        return ReplyKeyboardMarkup(
            keyboard=[row_1, row_2, row_cancel],
            resize_keyboard=True,
            input_field_placeholder=txt
        )

# reply кнопка донатов в webapp
def get_donate_button():
    markup = InlineKeyboardMarkup(
        row_width=1,
        inline_keyboard=[[InlineKeyboardButton(text='Поддержать проект',
                                               web_app=WebAppInfo(url=f'https://pay.cloudtips.ru/p/cbd68797'))
                          ]]
    )
    return markup


def webAppKeyboard():  # создание клавиатуры с webapp кнопкой
    keyboard = types.ReplyKeyboardMarkup(row_width=1)  # создаем клавиатуру
    webAppTest = types.WebAppInfo("https://telegram.mihailgok.ru")  # создаем webappinfo - формат хранения url
    one_butt = types.KeyboardButton(text="Тестовая страница", web_app=webAppTest)  # создаем кнопку типа webapp
    keyboard.add(one_butt)  # добавляем кнопки в клавиатуру

    return keyboard  # возвращаем клавиатуру
