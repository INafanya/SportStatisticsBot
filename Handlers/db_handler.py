import sqlite3
# import aiosqlite
import pandas as pd
from datetime import datetime, timedelta


# создание БД
# async def create_sql_db():
# async with aiosqlite.connect('mileage.db') as db:
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
                        category TEXT,
                        day_mileage FLOAT,
                        day_mileage_time INTEGER,
                        day_mileage_points FLOAT,
                        week_mileage FLOAT,
                        week_mileage_time INTEGER,
                        week_mileage_points FLOAT,
                        month_mileage FLOAT,
                        month_mileage_time INTEGER,
                        month_mileage_points FLOAT,
                        total_mileage FLOAT,
                        total_mileage_time INTEGER,
                        total_mileage_points FLOAT,
                        bid_category_man TEXT,
                        bid_mileage_man FLOAT,
                        bid_category_woman TEXT,
                        bid_mileage_woman FLOAT
                    )
                    ''')
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS points_mileage (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        username TEXT,
                        fullname TEXT,
                        gender TEXT,
                        category TEXT,
                        date DATE,
                        mileage FLOAT,
                        mileage_time INTEGER,
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
                        category TEXT,
                        date DATE,
                        mileage FLOAT,
                        mileage_time INTEGER,
                        points FLOAT
                    )
                    ''')
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS week_mileage (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        username TEXT,
                        fullname TEXT,
                        gender TEXT,
                        category TEXT,
                        week DATE,
                        mileage FLOAT,
                        mileage_time INTEGER,
                        points FLOAT
                    )
                    ''')
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS month_mileage (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        username TEXT,
                        fullname TEXT,
                        gender TEXT,
                        category TEXT,
                        month DATE,
                        mileage FLOAT,
                        mileage_time INTEGER,
                        points FLOAT
                    )
                    ''')
        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS day_club_mileage (
                                id INTEGER PRIMARY KEY,
                                category TEXT,
                                date DATE,
                                gender TEXT,
                                mileage FLOAT,
                                active_users INTEGER
                            )
                            ''')
        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS others_data (
                                id INTEGER PRIMARY KEY,
                                favorite INTEGER,
                                date DATE,
                                mileage INTEGER,
                                text_field_1 TEXT,
                                text_field_2 TEXT,
                                float_field_1 FLOAT,
                                float_field_2 FLOAT,
                                int_field_1 INTEGER,
                                int_field_2 INTEGER
                                    )
                                    ''')
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite при создании БД", error)
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
                day_mileage_points,
                week_mileage,
                week_mileage_time,
                week_mileage_points,
                month_mileage,
                month_mileage_time,
                month_mileage_points,
                total_mileage,
                total_mileage_time,
                total_mileage_points
            FROM users_mileage 
            WHERE telegram_id = ?
            ''', (telegram_id,), )
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite при чтении статистики пользователя", error)
    finally:
        if conn:
            user_statistics = cursor.fetchone()
            conn.close()
            return user_statistics


# получение основной информации по пользователю
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
            # print("Соединение с SQLite закрыто")
            return user_statistics


# добавление нового пользователя в БД
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
                        day_mileage_points,
                        week_mileage,
                        week_mileage_time,
                        week_mileage_points,
                        month_mileage,
                        month_mileage_time,
                        month_mileage_points,
                        total_mileage,
                        total_mileage_time,
                        total_mileage_points)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (telegram_id, username, fullname, gender, category, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        )
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.commit()
            conn.close()
            # print("Соединение с SQLite закрыто")


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
    if abs(new_mileage) <= 1:
        coeff = 0.7943
    elif 1 < abs(new_mileage) <= 10:
        coeff = pow(abs(new_mileage) / 10, 0.1)
    elif 10 < abs(new_mileage) <= 42:
        coeff = pow(abs(new_mileage) / 10, 0.12)
    else:
        coeff = 1.1879 + (abs(new_mileage) - 42) * 0.00912506
    # коэффициент пола
    if gender == 'девушка':
        gender_coeff = 72
    else:
        gender_coeff = 60
    # расчет скорости с учетом коэффициента и пола
    speed = (gender_coeff * abs(new_mileage) * coeff) * 60 / abs(new_mileage_time)
    if speed > 19.46:
        speed = 19.46
    # поиск ближайшей минимальной скорости из списка
    speed_points_keys = list(speed_points.keys())
    for i in range(0, len(speed_points_keys)):
        if speed_points_keys[i] // speed:
            speed_min = speed_points_keys[i - 1]
            speed_max = speed_points_keys[i]
            break
    # величина интервала
    interval = speed_max - speed_min
    # дробная часть баллов
    if interval:
        points_dop = (speed - speed_min) / interval
    else:
        points_dop = speed - speed_min
    # баллы с учетом дистанции
    if speed < 6.666666667:
        points_finish = 0
    else:
        points_finish = (speed_points.get(speed_min) + points_dop) * abs(new_mileage) / 10
    today = datetime.now().strftime('%d.%m.%Y')
    if new_mileage < 0:
        points_finish = -points_finish
    sql_txt = f'''INSERT INTO points_mileage
                (telegram_id, username, fullname, gender, category, date, mileage, mileage_time, points)
                VALUES ({telegram_id}, '{username}', '{fullname}', '{gender}', '{category}', 
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
        return points_finish


# обновление дневного пробега в БД
def update_day_data_db(telegram_id: int, new_mileage: float, new_mileage_time: int, new_mileage_points: float):
    # получаем результат запроса статистики пользователя
    user_statistics = read_user_statistics_from_db(telegram_id)

    username, fullname, gender, category, day_mileage, day_mileage_time, day_mileage_points, week_mileage, \
        week_mileage_time, week_mileage_points, month_mileage, month_mileage_time, month_mileage_points, \
        total_mileage, total_mileage_time, total_mileage_points = user_statistics
    # проверка на отрицательное значение, если новый пробег отрицательный и больше текущего,
    # то сбрасывается текущий пробег
    if day_mileage + new_mileage < 0:
        week_mileage -= day_mileage
        month_mileage -= day_mileage
        total_mileage -= day_mileage
        week_mileage_time -= day_mileage_time
        month_mileage_time -= day_mileage_time
        total_mileage_time -= day_mileage_time
        week_mileage_points -= day_mileage_points
        month_mileage_points -= day_mileage_points
        total_mileage_points -= day_mileage_points
        day_mileage = 0
        day_mileage_time = 0
        day_mileage_points = 0
    else:
        day_mileage += new_mileage
        week_mileage += new_mileage
        month_mileage += new_mileage
        total_mileage += new_mileage
        day_mileage_time += new_mileage_time
        week_mileage_time += new_mileage_time
        month_mileage_time += new_mileage_time
        total_mileage_time += new_mileage_time
        day_mileage_points += new_mileage_points
        week_mileage_points += new_mileage_points
        month_mileage_points += new_mileage_points
        total_mileage_points += new_mileage_points
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
                    day_mileage_points = ?,
                    week_mileage = ?,
                    week_mileage_time = ?,
                    week_mileage_points = ?,
                    month_mileage = ?,
                    month_mileage_time = ?,
                    month_mileage_points = ?,
                    total_mileage = ?,
                    total_mileage_time = ?,
                    total_mileage_points = ?
                    WHERE 
                    telegram_id = ?
                    ''',
                       (username,
                        fullname,
                        gender,
                        category,
                        day_mileage,
                        day_mileage_time,
                        day_mileage_points,
                        week_mileage,
                        week_mileage_time,
                        week_mileage_points,
                        month_mileage,
                        month_mileage_time,
                        month_mileage_points,
                        total_mileage,
                        total_mileage_time,
                        total_mileage_points,
                        telegram_id)
                       )
        conn.commit()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()
            # print("Соединение с SQLite закрыто")
        return day_mileage, day_mileage_time, day_mileage_points


def update_favorite_mileage(favorite, mileage_km):
    today = datetime.now().strftime('%d.%m.%Y')
    sql_txt = f'''INSERT INTO others_data (date, favorite, mileage) VALUES ('{today}', {favorite}, {mileage_km})'''
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


# внесение ставки в БД
def update_bid(telegram_id: int, bid_man_category: str, bid_man: float, bid_woman_category: str, bid_woman: float):
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        cursor.execute('''
                    UPDATE users_mileage 
                    SET 
                    bid_category_man = ?,
                    bid_mileage_man = ?,
                    bid_category_woman = ?,
                    bid_mileage_woman = ?
                    WHERE 
                    telegram_id = ?
                    ''',
                       (bid_man_category,
                        bid_man,
                        bid_woman_category,
                        bid_woman,
                        telegram_id)
                       )
        conn.commit()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()


# копирование и отчистка дневной статистики
def copy_and_clear_day_mileage():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
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
            day_mileage_time,
            day_mileage_points
            FROM users_mileage
            ''')
        result_db = cursor.fetchall()
        sql_query = '''INSERT INTO day_mileage
                        (telegram_id , username, fullname, gender, category, date, mileage, mileage_time, points)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        cursor.executemany(sql_query, result_db)
        conn.commit()
        # удаляем дневную статистику в таблице users_mileage
        cursor.execute('''
            UPDATE users_mileage 
            SET day_mileage = 0, day_mileage_time = 0, day_mileage_points = 0
            ''')
        conn.commit()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()


# отчистка недельной статистики
def copy_and_clear_week_mileage():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        # копируем недельную статистику в таблицу week_mileage
        cursor.execute('''
                    SELECT
                    telegram_id,
                    username,
                    fullname,
                    gender,
                    category,
                    strftime('%W', datetime('now')) as date,
                    week_mileage,
                    week_mileage_time,
                    week_mileage_points
                    FROM users_mileage
                    ''')
        result_db = cursor.fetchall()
        sql_query = '''INSERT INTO week_mileage
                       (telegram_id , username, fullname, gender, category, week, mileage, mileage_time, points)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        cursor.executemany(sql_query, result_db)
        conn.commit()
        # удаляем недельную статистику в таблице users_mileage
        cursor.execute('''UPDATE users_mileage
                            SET week_mileage = 0, week_mileage_time = 0, week_mileage_points = 0''')
        # сохраняем изменения в базе данных
        conn.commit()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()


# отчистка месячной статистики
def copy_and_clear_month_mileage():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        # копируем месячную статистику в таблицу month_mileage
        cursor.execute('''
                    SELECT 
                    telegram_id,
                    username,
                    fullname,
                    gender,
                    category,
                    strftime('%m', datetime('now')) as date,
                    month_mileage,
                    month_mileage_time,
                    month_mileage_points
                    FROM users_mileage
                    ''')
        result_db = cursor.fetchall()
        sql_query = '''INSERT INTO month_mileage
                        (telegram_id , username, fullname, gender, category, month, mileage, mileage_time, points)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        cursor.executemany(sql_query, result_db)
        conn.commit()
        # удаляем месячную статистику в таблице users_mileage
        cursor.execute(
            '''UPDATE users_mileage SET month_mileage = 0, month_mileage_time = 0, month_mileage_points = 0''')
        # сохраняем изменения в базе данных
        conn.commit()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()


def copy_day_club_mileage():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        today = get_today()
        # получение кол-ва парней в минимальном клубе
        cursor.execute('''
                                        SELECT
                                        count(telegram_id), category
                                        FROM users_mileage
                                        WHERE gender = 'парень'
                                        GROUP BY category
                                        ORDER BY count(telegram_id)
                                        ''', )
        min_club_count_man = cursor.fetchone()[0]
        if not min_club_count_man:
            min_club_count_man = 1
        # получение кол-ва девушек в минимальном клубе
        cursor.execute('''
                                                SELECT
                                                count(telegram_id), category
                                                FROM users_mileage
                                                WHERE gender = 'девушка'
                                                GROUP BY category
                                                ORDER BY count(telegram_id)
                                                ''', )
        min_club_count_woman = cursor.fetchone()[0]
        if not min_club_count_woman:
            min_club_count_woman = 1
        # сумма пробега у n лучших парней клуба
        cursor.execute('''
                                SELECT category,
                                        date,
                                        gender,
                                        sum(mileage) mileage,
                                        %s as active_users 
                                FROM day_mileage a 
                                WHERE a.id IN (
                                              SELECT id FROM day_mileage b 
                                              WHERE b.category = a.category
                                              AND b.gender = 'парень' 
                                              AND b.date = '%s'
                                              ORDER BY b.category, b.mileage DESC 
                                              LIMIT %s)
                                GROUP BY category
                                ORDER BY sum(mileage) DESC
                                        ''' % (min_club_count_man, today, min_club_count_man), )
        club_mileage_man = cursor.fetchall()

        # сумма пробега у n лучших девушек клуба
        cursor.execute('''
                                    SELECT category,
                                            date,
                                            gender,
                                            sum(mileage) mileage,
                                            %s as active_users 
                                    FROM day_mileage a 
                                    WHERE a.id IN (
                                                  SELECT id FROM day_mileage b 
                                                  WHERE b.category = a.category
                                                  AND b.gender = 'девушка' 
                                                  AND b.date = '%s'
                                                  ORDER BY b.category, b.mileage DESC 
                                                  LIMIT %s)
                                    GROUP BY category
                                    ORDER BY sum(mileage) DESC
                                            ''' % (min_club_count_woman, today, min_club_count_woman), )
        club_mileage_woman = cursor.fetchall()

        # записываем полученный рейтинг и кол-во человек в таблицу day_club_mileage
        sql_query = '''INSERT INTO day_club_mileage (category, date, gender, mileage, active_users)
                                        VALUES (?, ?, ?, ?, ?)'''
        cursor.executemany(sql_query, club_mileage_man)
        conn.commit()
        cursor.executemany(sql_query, club_mileage_woman)
        conn.commit()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()


def read_day_rating():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        yesterday = get_yesterday()
        cursor.execute('''
                SELECT 
                telegram_id,
                fullname,
                category,
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
        return results


def read_club_rating():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        # получение суммарного мужского пробега по клубам
        cursor.execute('''SELECT
                            category, sum(mileage) as sum_mileage
                            FROM day_club_mileage
                            WHERE gender = 'парень'
                            GROUP BY category
                            ORDER BY sum(mileage) DESC
                        ''', )
        man_rating = cursor.fetchall()
        # получение суммарного женского пробега по клубам
        cursor.execute('''SELECT
                                    category, sum(mileage) as sum_mileage
                                    FROM day_club_mileage
                                    WHERE gender = 'девушка'
                                    GROUP BY category
                                    ORDER BY sum(mileage) DESC
                                ''', )
        woman_rating = cursor.fetchall()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()
        return man_rating, woman_rating


def read_day_time_rating():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        yesterday = get_yesterday()
        cursor.execute('''
                SELECT 
                telegram_id,
                fullname,
                mileage_time
                FROM day_mileage
                WHERE date = ? AND mileage > 0
                ORDER BY mileage_time DESC
                ''', (yesterday,), )
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            results = cursor.fetchall()
            conn.close()
        return results


def read_day_points_rating():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        yesterday = get_yesterday()
        cursor.execute('''
                SELECT 
                telegram_id,
                fullname,
                points
                FROM day_mileage
                WHERE date = ? AND mileage > 0
                ORDER BY points DESC
                ''', (yesterday,), )
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            results = cursor.fetchall()
            conn.close()
        return results


def read_week_rating():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        yesterweek = get_yesterweek()
        cursor.execute('''
                    SELECT 
                    telegram_id,
                    fullname,
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
        return results


def read_week_time_rating():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        yesterweek = get_yesterweek()
        cursor.execute('''
                SELECT 
                telegram_id,
                fullname,
                mileage_time
                FROM week_mileage
                WHERE week = ? AND mileage > 0
                ORDER BY mileage_time DESC
                ''', (yesterweek,), )
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            results = cursor.fetchall()
            conn.close()
        return results


def read_week_points_rating():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        yesterweek = get_yesterweek()
        cursor.execute('''
                SELECT 
                telegram_id,
                fullname,
                points
                FROM week_mileage
                WHERE week = ? AND mileage > 0
                ORDER BY points DESC
                ''', (yesterweek,), )
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            results = cursor.fetchall()
            conn.close()
        return results


def read_month_rating():  # исправить
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
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
        return winners + loosers[::-1] + users_sum


def get_today():
    date_format = '%d.%m.%Y'
    today = datetime.now()
    today_format = today.strftime(date_format)
    return today_format


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


# получение ставки по пользователю
def read_user_bids_from_db(telegram_id: int):
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                username,
                fullname,
                gender,
                category,
                bid_category_man,
                bid_mileage_man,
                bid_category_woman,
                bid_mileage_woman
            FROM users_mileage 
            WHERE telegram_id = ?
            ''', (telegram_id,), )
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite при чтении статистики пользователя", error)
    finally:
        if conn:
            user_bids = cursor.fetchone()
            conn.close()
            return user_bids


def export_data_to_file():
    try:
        conn = sqlite3.connect('mileage.db')
        club_rating = pd.read_sql('SELECT * FROM day_club_mileage', conn)
        points_mileage = pd.read_sql('SELECT * FROM points_mileage', conn)
        users_mileage_today = pd.read_sql('SELECT * FROM users_mileage', conn)
        days_mileage = pd.read_sql('SELECT * FROM day_mileage', conn)
        week_mileage = pd.read_sql('SELECT * FROM week_mileage', conn)
        favorites_mileage = pd.read_sql('''SELECT date as Дата, favorite as Фаворит, sum(mileage) as Пробег
                                            FROM others_data''', conn)
        filename = f"Day_mileage_{datetime.now().strftime('%d.%m.%Y_%H_%M')}.xlsx"
        df_1 = pd.read_sql('''SELECT username as Парни_Казбек, total_mileage as Пробег
                            FROM users_mileage
                            WHERE gender = 'парень' AND category = 'Казбек' AND total_mileage > 0
                            ORDER BY total_mileage DESC 
                            ''', conn)
        df_2_start_row = df_1.shape[0] + 3
        df_2 = pd.read_sql('''SELECT username as Парни_Эльбрус, total_mileage as Пробег
                            FROM users_mileage
                            WHERE gender = 'парень' AND category = 'Эльбрус' AND total_mileage > 0
                            ORDER BY total_mileage DESC 
                            ''', conn)
        df_3_start_row = df_2_start_row + df_2.shape[0] + 3
        df_3 = pd.read_sql('''SELECT username as Парни_3, total_mileage as Пробег
                            FROM users_mileage
                            WHERE gender = 'парень' AND category = 3 AND total_mileage > 0
                            ORDER BY total_mileage DESC 
                            ''', conn)

        df_4 = pd.read_sql('''SELECT username as Девушки_Казбек, total_mileage as Пробег
                            FROM users_mileage
                            WHERE gender = 'девушка' AND category = 'Казбек' AND total_mileage > 0
                            ORDER BY total_mileage DESC 
                            ''', conn)
        df_5_start_row = df_4.shape[0] + 3
        df_5 = pd.read_sql('''SELECT username as Девушки_Эльбрус, total_mileage as Пробег
                            FROM users_mileage
                            WHERE gender = 'девушка' AND category = 'Эльбрус' AND total_mileage > 0
                            ORDER BY total_mileage DESC 
                            ''', conn)
        df_6_start_row = df_5.shape[0] + df_5_start_row + 3
        df_6 = pd.read_sql('''SELECT username as Девушки_3, total_mileage as Пробег
                            FROM users_mileage
                            WHERE gender = 'девушка' AND category = 3 AND total_mileage > 0
                            ORDER BY total_mileage DESC 
                            ''', conn)
        df_7_start_row = df_3.shape[0] + df_3_start_row + 3
        df_7 = pd.read_sql('''SELECT username as Имя, total_mileage_time as Суммарное_время
                                    FROM users_mileage
                                    WHERE total_mileage_time > 0
                                    ORDER BY total_mileage_time DESC 
                                    ''', conn)
        df_8_start_row = df_6.shape[0] + df_6_start_row + 3
        df_8 = pd.read_sql('''SELECT username as Имя, round(total_mileage_points, 2) as Суммарные_баллы
                                            FROM users_mileage
                                            WHERE total_mileage_points > 0
                                            ORDER BY total_mileage_points DESC 
                                            ''', conn)
        with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
            users_mileage_today.to_excel(writer, sheet_name='Суммарная статистика', index=False)
            points_mileage.to_excel(writer, sheet_name='Статистика по каждому пробегу', index=False)
            days_mileage.to_excel(writer, sheet_name='Пробеги по дням', index=False)
            week_mileage.to_excel(writer, sheet_name='Пробеги по неделям', index=False)
            club_rating.to_excel(writer, sheet_name='Клубный рейтинг', index=False)
            favorites_mileage.to_excel(writer, sheet_name='Дед Мороз и Снегурочка', index=False)
            df_1.to_excel(writer, sheet_name='Сводные таблицы', index=False)
            df_2.to_excel(writer, sheet_name='Сводные таблицы', index=False, startrow=df_2_start_row)
            df_3.to_excel(writer, sheet_name='Сводные таблицы', index=False, startrow=df_3_start_row)
            df_4.to_excel(writer, sheet_name='Сводные таблицы', index=False, startcol=4)
            df_5.to_excel(writer, sheet_name='Сводные таблицы', index=False, startcol=4, startrow=df_5_start_row)
            df_6.to_excel(writer, sheet_name='Сводные таблицы', index=False, startcol=4, startrow=df_6_start_row)
            df_7.to_excel(writer, sheet_name='Сводные таблицы', index=False, startrow=df_7_start_row)
            df_8.to_excel(writer, sheet_name='Сводные таблицы', index=False, startcol=4, startrow=df_8_start_row)

    except PermissionError as error:
        print(f"Ошибка экспорта, {error}")
    finally:
        if conn:
            conn.close()
        return filename
