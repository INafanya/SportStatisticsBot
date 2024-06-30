import sqlite3
import pandas as pd
from datetime import datetime, timedelta


# создание БД
def create_sql_db():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users_mileage (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        username TEXT,
                        fullname TEXT,
                        gender TEXT,
                        category INTEGER,
                        day_mileage FLOAT,
                        day_mileage_time FLOAT,
                        day_mileage_points FLOAT,
                        week_mileage FLOAT,
                        week_mileage_time FLOAT,
                        week_mileage_points FLOAT,
                        month_mileage FLOAT,
                        month_mileage_time FLOAT,
                        month_mileage_points FLOAT,
                        total_mileage FLOAT,
                        total_mileage_time FLOAT,
                        total_mileage_points FLOAT
                    )
                    ''')
        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS points_mileage (
                                id INTEGER PRIMARY KEY,
                                telegram_id INTEGER,
                                username TEXT,
                                fullname TEXT,
                                gender TEXT,
                                category INTEGER,
                                date DATE,
                                mileage FLOAT,
                                mileage_time FLOAT,
                                points FLOAT
                            )
                            ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS day_mileage (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        username TEXT,
                        fullname TEXT,
                        gender TEXT,
                        category INTEGER,
                        date DATE,
                        mileage FLOAT,
                        mileage_time FLOAT,
                        points FLOAT
                    )
                    ''')
        # print("Создана таблица day_mileage")
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS week_mileage (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        username TEXT,
                        fullname TEXT,
                        gender TEXT,
                        category INTEGER,
                        week DATE,
                        mileage FLOAT,
                        mileage_time FLOAT,
                        points FLOAT
                    )
                    ''')
        # print("Создана таблица week_mileage")
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS month_mileage (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        username TEXT,
                        fullname TEXT,
                        gender TEXT,
                        category INTEGER,
                        month DATE,
                        mileage FLOAT,
                        mileage_time FLOAT,
                        points FLOAT
                    )
                    ''')
        # print("Создана таблица month_mileage")
        # cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Есть БД. Соединение с SQLite закрыто")


# запрос статистики по пользователю
def read_user_statistics_from_db(telegram_id: int):
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
            username,
            fullname,
            gender,
            category,
            day_mileage,
            day_mileage_time,
            week_mileage,
            week_mileage_time,
            month_mileage,
            month_mileage_time,
            total_mileage,
            total_mileage_time
            FROM users_mileage 
            WHERE telegram_id = ?
            ''', (telegram_id,), )

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            user_statistics = cursor.fetchone()
            conn.close()
            print("Соединение с SQLite закрыто")
            return user_statistics

# Новая версия запроса сегодняшней статистики по пользователю с балами
def read_user_from_db(telegram_id: int):
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
            username,
            fullname,
            gender,
            category
            FROM users_mileage
            WHERE telegram_id = ?
            ''', (telegram_id,), )

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            user_statistics = cursor.fetchone()
            conn.close()
            print("Соединение с SQLite закрыто")
            return user_statistics

def add_new_user(telegram_id: int, username: str, fullname: str, gender: str, category: str):
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        # добавляем новую запись в таблицу users_mileage
        cursor.execute(
            '''
            INSERT INTO users_mileage(
                        telegram_id,
                        username,
                        fullname,
                        gender,
                        category,
                        day_mileage,
                        day_mileage_time,
                        week_mileage,
                        week_mileage_time,
                        month_mileage,
                        month_mileage_time,
                        total_mileage,
                        total_mileage_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (telegram_id, username, fullname, gender, category, 0, 0, 0, 0, 0, 0, 0, 0,)
                    )
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.commit()
            conn.close()
            print("Соединение с SQLite закрыто")


# обновление дневного пробега в БД
def update_day_data_db(telegram_id: int, new_mileage: float, new_mileage_time: int):
    # получаем результат запроса статистики пользователя
    user_statistics = read_user_statistics_from_db(telegram_id)
    # обновляем дневной пробег пользователя
    username, fullname, gender, category, day_mileage, day_mileage_time, week_mileage, week_mileage_time, \
        month_mileage, month_mileage_time, total_mileage, total_mileage_time = user_statistics
    # проверка на отрицательное значение, если новый побег отрицательный и больше текущего,
    # то сбрасывается текущий пробег
    if day_mileage + new_mileage < 0:
        week_mileage -= day_mileage
        month_mileage -= day_mileage
        total_mileage -= day_mileage
        week_mileage_time -= day_mileage_time
        month_mileage_time -= day_mileage_time
        total_mileage_time -= day_mileage_time
        day_mileage = 0
        day_mileage_time = 0
    else:
        day_mileage += new_mileage
        week_mileage += new_mileage
        month_mileage += new_mileage
        total_mileage += new_mileage
        day_mileage_time += new_mileage_time
        week_mileage_time += new_mileage_time
        month_mileage_time += new_mileage_time
        total_mileage_time += new_mileage_time

    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        cursor.execute('''
                    UPDATE users_mileage 
                    SET 
                    username = ?,
                    fullname = ?,
                    gender = ?,
                    category = ?,
                    day_mileage = ?,
                    day_mileage_time = ?,
                    week_mileage = ?,
                    week_mileage_time = ?,
                    month_mileage = ?,
                    month_mileage_time = ?,
                    total_mileage = ?,
                    total_mileage_time = ?
                    WHERE 
                    telegram_id = ?
                    ''',
                       (username,
                        fullname,
                        gender,
                        category,
                        day_mileage,
                        day_mileage_time,
                        week_mileage,
                        week_mileage_time,
                        month_mileage,
                        month_mileage_time,
                        total_mileage,
                        total_mileage_time,
                        telegram_id)
                       )
        conn.commit()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")

        return day_mileage, day_mileage_time


# обновление дневного пробега текущего дня в БД с вычислением балов
def update_today_data_db(telegram_id: int, new_mileage: float, new_mileage_time: int):
    speed_points = {
        6.666666667: 0,
        7.058823529: 1,
        7.5: 2,
        8.0: 3,
        8.571428571: 4,
        9.230769231: 5,
        10.0: 6,
        10.90909091: 7,
        12.0: 8,
        13.33333333: 9,
        15.50387597: 10,
        16.90140845: 11,
        18.09408926: 12,
        19.46156341: 13,
    }

    # получение данных пользователя
    user = read_user_from_db(telegram_id)
    username, fullname, gender, category = user

    # расчет коэффициента с учетом расстояния
    if new_mileage <= 1:
        coeff = 0.7943
    elif 1 < new_mileage <= 10:
        coeff = pow(new_mileage/10, 0.1)
    elif 10 < new_mileage <= 42:
        coeff = pow(new_mileage/10, 0.12)
    else:
        coeff = 1.1879 + (new_mileage - 42) * 0.00912506
    #print(f"coeff = {coeff}")
    #print(f"new_mileage = {new_mileage}")
    #print(f"new_mileage_time = {new_mileage_time}")

    # расчет скорости с учетом коэффициента и пола
    if gender == 'царевна':
        speed = (72 * new_mileage * coeff) / new_mileage_time
    else:
        speed = (60 * new_mileage * coeff) / new_mileage_time
    #print(f"speed = {speed}")

    # поиск ближайшей минимальной скорости из списка
    speed_points_keys = list(speed_points.keys())
    for i in range(0, len(speed_points_keys)):
        if speed_points_keys[i] // speed:
            speed_min = speed_points_keys[i - 1]
            speed_max = speed_points_keys[i]
            #print(f"speed_min = {speed_min}")
            #print(f"speed_max = {speed_max}")
            break

    # величина интервала
    interval = speed_max - speed_min
    # дробная часть баллов
    if interval:
        points_dop = (speed - speed_min) / interval
    else:
        points_dop = speed - speed_min
    #print(f"interval = {interval}")
    #print(f"points_dop = {points_dop}")

    # баллы с учетом дистанции
    points_finish = (speed_points.get(speed_min) + points_dop) * new_mileage / 10
    #print(f"points_finish = {points_finish}")


    today = datetime.now().strftime('%d.%m.%Y')

    sql_txt = f'''INSERT INTO points_mileage
                (telegram_id, username, fullname, gender, category, date, mileage, mileage_time, points)
                VALUES ({telegram_id}, '{username}', '{fullname}', '{gender}', {category}, 
                '{today}', {new_mileage}, {new_mileage_time}, {points_finish})'''
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        cursor.execute(sql_txt)
        conn.commit()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")
        return points_finish

# копирование и отчистка дневной статистики
def copy_and_clear_day_mileage():
    try:
        print("Старт обнуления дневной статистики")
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        print("Подключение к SQLite успешно")
        print("Сохраняю дневную статистику")
        # копируем дневную статистику в таблицу day_mileage
        cursor.execute('''
            SELECT 
            telegram_id,
            username,
            fullname,
            gender,
            category,
            strftime('%d.%m.%Y', datetime('now')) as date,
            day_mileage,
            day_mileage_time
            FROM users_mileage
            ''')

        result_db = cursor.fetchall()

        sql_query = '''INSERT INTO day_mileage
                        (telegram_id , username, fullname, gender, category, date, mileage, mileage_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''

        cursor.executemany(sql_query, result_db)
        conn.commit()

        print("Записи успешно вставлены в таблицу", cursor.rowcount)

        # удаляем дневную статистику в таблице users_mileage
        print("Обнуляю дневную статистику")
        cursor.execute('''
            UPDATE users_mileage 
            SET day_mileage = 0, day_mileage_time = 0
            ''')
        conn.commit()
        print("Обнуление дневной статистики завершено")

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")


# отчистка недельной статистики
def copy_and_clear_week_mileage():
    try:
        print("Старт обнуления недельной статистики")
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        print("Подключение к SQLite успешно")
        print("Сохраняю недельную статистику")
        # копируем недельную статистику в таблицу week_mileage
        cursor.execute('''
                    SELECT
                    telegram_id,
                    username,
                    strftime('%W', datetime('now')) as date,
                    week_mileage
                    FROM users_mileage
                    ''')

        result_db = cursor.fetchall()

        sql_query = '''INSERT INTO week_mileage
                       (telegram_id , username, week, mileage)
                       VALUES (?, ?, ?, ?)'''

        cursor.executemany(sql_query, result_db)
        conn.commit()
        print("Записи успешно вставлены в таблицу", cursor.rowcount)

        # удаляем недельную статистику в таблице users_mileage
        cursor.execute('''UPDATE users_mileage SET week_mileage = 0''')

        # сохраняем изменения в базе данных
        conn.commit()
        # cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")


# отчистка месячной статистики
def copy_and_clear_month_mileage():
    try:
        print("Старт обнуления месячной статистики")
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        print("Подключение к SQLite успешно")
        print("Сохраняю месячную статистику")
        # копируем месячную статистику в таблицу month_mileage
        cursor.execute('''
                    SELECT 
                    telegram_id,
                    username,
                    strftime('%m', datetime('now')) as date,
                    month_mileage
                    FROM users_mileage
                    ''')

        result_db = cursor.fetchall()

        sql_query = '''INSERT INTO month_mileage
                                (telegram_id , username, month, mileage)
                                VALUES (?, ?, ?, ?)'''

        cursor.executemany(sql_query, result_db)
        conn.commit()
        print("Записи успешно вставлены в таблицу", cursor.rowcount)

        # удаляем месячную статистику в таблице users_mileage
        cursor.execute('''UPDATE users_mileage SET month_mileage = 0''')

        # сохраняем изменения в базе данных
        conn.commit()
        # cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")


def read_day_rating():
    try:
        print("Считываю дневной рейтинг")
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        print("Подключение к SQLite успешно")
        yesterday = get_yesterday()
        cursor.execute('''
                SELECT 
                telegram_id,
                fullname,
                mileage
                FROM day_mileage
                WHERE date = ? AND mileage > 0
                ORDER BY mileage DESC
                ''', (yesterday,), )

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            results = cursor.fetchall()
            conn.close()
            print("Дневной рейтинг считан")
            print("Соединение с SQLite закрыто")
        return results

def read_day_time_rating():
    try:
        print("Считываю дневной рейтинг")
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        print("Подключение к SQLite успешно")
        yesterday = get_yesterday()
        cursor.execute('''
                SELECT 
                telegram_id,
                fullname,
                mileage_time
                FROM day_mileage
                WHERE date = ? AND mileage > 0
                ORDER BY mileage DESC
                ''', (yesterday,), )

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            results = cursor.fetchall()
            conn.close()
            print("Дневной рейтинг считан")
            print("Соединение с SQLite закрыто")
        return results


def read_week_rating(): #исправить
    try:
        print("Считываю недельный рейтинг")
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        print("Подключение к SQLite успешно")
        yesterweek = get_yesterweek()
        cursor.execute('''
                    SELECT 
                    telegram_id,
                    username,
                    mileage
                    FROM week_mileage
                    WHERE week = ? AND mileage > 0
                    ORDER BY mileage DESC
                    ''', (yesterweek,), )
        results = cursor.fetchall()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Недельный рейтинг считан")
            print("Соединение с SQLite закрыто")
        return results


def read_month_rating(): # исправить
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        print("Подключение к SQLite успешно")

        cursor.execute('''
                    SELECT 
                    COUNT(telegram_id)
                    FROM month_mileage
                    ''')

        users_sum = cursor.fetchall()

        cursor.execute('''
            SELECT 
            telegram_id,
            username,
            mileage
            FROM month_mileage
            ORDER BY mileage DESC
            LIMIT 5
            ''')

        winners = cursor.fetchall()

        cursor.execute('''
                    SELECT 
                    telegram_id,
                    username,
                    mileage
                    FROM month_mileage
                    WHERE mileage > 0
                    ORDER BY mileage ASC
                    LIMIT 3
                    ''')
        loosers = cursor.fetchall()

        # cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")
        return winners + loosers[::-1] + users_sum


def get_yesterday():
    date_format = '%d.%m.%Y'
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_format = yesterday.strftime(date_format)
    return yesterday_format


def get_yesterweek():
    date_format = '%V'
    yesterweek = datetime.now() - timedelta(days=7)
    yesterweek_format = yesterweek.strftime(date_format)
    return yesterweek_format


def export_data_to_file():
    try:
        conn = sqlite3.connect('mileage.db')
        db_data = pd.read_sql('SELECT * FROM day_mileage', conn)
        filename = f"Day_mileage_{datetime.now().strftime('%d.%m.%Y_%H_%M')}.xlsx"
        db_data.to_excel(fr'{filename}', index=False)

    except PermissionError as error:
        print(f"Ошибка экспорта, {error}")
    finally:
        if conn:
            conn.close()
            print("Экспорт данных из БД в файл закончен")
        return filename
