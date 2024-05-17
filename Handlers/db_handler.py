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
                        day_mileage FLOAT,
                        week_mileage FLOAT,
                        month_mileage FLOAT,
                        total_mileage FLOAT
                    )
                    ''')
        # print("Создана таблица users_mileage")
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS day_mileage (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        username TEXT,
                        date DATE,
                        day_mileage FLOAT
                    )
                    ''')
        # print("Создана таблица day_mileage")
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS week_mileage (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        username TEXT,
                        week DATE,
                        week_mileage FLOAT
                    )
                    ''')
        # print("Создана таблица week_mileage")
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS month_mileage (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        username TEXT,
                        month DATE,
                        month_mileage FLOAT
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


# добавление нового юзера в таблицу users_mileage
def add_data_db(telegram_id: int, username: str, new_mileage: float):
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        username = username
        # добавляем новую запись в таблицу users_mileage
        cursor.execute('''
            INSERT INTO users_mileage(
                        telegram_id,
                        username,
                        day_mileage,
                        week_mileage,
                        month_mileage,
                        total_mileage)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''',
                       (telegram_id,
                        username,
                        new_mileage,
                        new_mileage,
                        new_mileage,
                        new_mileage)
                       )

        # сохраняем изменения в базе данных
        conn.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")


# запрос статистики по пользователю
def read_user_statistics_from_db(telegram_id: int):
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
            username,
            day_mileage,
            week_mileage,
            month_mileage,
            total_mileage
            FROM users_mileage 
            WHERE telegram_id = ?
            ''', (telegram_id,), )
        # cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            user_statistics = cursor.fetchone()
            conn.close()
            print("Соединение с SQLite закрыто")
            return user_statistics


# обновление дневного пробега в БД
def update_day_data_db(telegram_id: int, username: str, new_mileage: float):
    # получаем результат запроса статистики пользователя
    user_statistics = read_user_statistics_from_db(telegram_id)
    # проверяем есть ли пользователь в БД, если нет добавляем пользователя в БД
    if not user_statistics:
        if new_mileage < 0:
            new_mileage = 0
        add_data_db(telegram_id, username, new_mileage)
        user_statistics = read_user_statistics_from_db(telegram_id)
        username, day_mileage, week_mileage, month_mileage, total_mileage = user_statistics
        print(f"новый пользователь, пробег: {new_mileage}")
    else:
        # обновляем дневной пробег пользователя
        username, day_mileage, week_mileage, month_mileage, total_mileage = user_statistics
        # проверка на отрицательное значение
        if day_mileage + new_mileage > 0:
            day_mileage += new_mileage
            week_mileage += new_mileage
            month_mileage += new_mileage
            total_mileage += new_mileage
        else:
            week_mileage -= day_mileage
            month_mileage -= day_mileage
            total_mileage -= day_mileage
            day_mileage = 0
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        cursor.execute('''
                    UPDATE users_mileage 
                    SET 
                    username = ?,
                    day_mileage = ?,
                    week_mileage = ?,
                    month_mileage = ?,
                    total_mileage = ?
                    WHERE 
                    telegram_id = ?
                    ''',
                       (username,
                        day_mileage,
                        week_mileage,
                        month_mileage,
                        total_mileage,
                        telegram_id)
                       )
        conn.commit()
        # cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")
        return day_mileage


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
            strftime('%d.%m.%Y', datetime('now')) as date,
            day_mileage
            FROM users_mileage
            ''')

        result_db = cursor.fetchall()

        sql_query = '''INSERT INTO day_mileage
                        (telegram_id , username, date, day_mileage)
                        VALUES (?, ?, ?, ?)'''

        cursor.executemany(sql_query, result_db)
        conn.commit()

        print("Записи успешно вставлены в таблицу", cursor.rowcount)

        # удаляем дневную статистику в таблице users_mileage
        print("Обнуляю дневную статистику")
        cursor.execute('''
            UPDATE users_mileage 
            SET day_mileage = 0
            ''')
        conn.commit()
        print("Обнуление дневной статистики завершено")


    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")
            # cmd_day_rating()


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
                    usernsme,
                    strftime('%W', datetime('now')) as date,
                    week_mileage
                    FROM users_mileage
                    ''')

        result_db = cursor.fetchall()

        sql_query = '''INSERT INTO week_mileage
                       (telegram_id , username, week, week_mileage)
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
                                (telegram_id , username, month, month_mileage)
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
        # users_sum = cursor.fetchall()
        cursor.execute('''
                SELECT 
                telegram_id,
                username,
                day_mileage
                FROM day_mileage
                WHERE date = ? AND day_mileage > 0
                ORDER BY day_mileage DESC
                ''', (yesterday,), )

        results = cursor.fetchall()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Дневной рейтинг считан")
            print("Соединение с SQLite закрыто")
        return results


def read_week_rating():
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
                    week_mileage
                    FROM week_mileage
                    WHERE week = ? AND week_mileage > 0
                    ORDER BY week_mileage DESC
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


def read_month_rating():
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
            month_mileage
            FROM month_mileage
            ORDER BY month_mileage DESC
            LIMIT 5
            ''')

        winners = cursor.fetchall()

        cursor.execute('''
                    SELECT 
                    telegram_id,
                    username,
                    month_mileage
                    FROM month_mileage
                    WHERE month_mileage > 0
                    ORDER BY month_mileage ASC
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
    print("Начинаю экспорт данных из БД в файл")
    # db_data = read_day_rating()
    # filename = (datetime.now()).strftime('%d.%m.%Y_%hh.%mm')
    try:
        conn = sqlite3.connect('mileage.db')
        db_data = pd.read_sql('SELECT id, telegram_id, username, date, day_mileage FROM day_mileage', conn)
        filename = f"Day_mileage_{datetime.now().strftime('%d.%m.%Y_%H_%M')}.xlsx"
        db_data.to_excel(fr'{filename}', index=False)

    except PermissionError as error:
        print(f"Ошибка экспорта, {error}")
    finally:
        if conn:
            conn.close()
            print("Экспорт данных из БД в файл закончен")
        return filename
