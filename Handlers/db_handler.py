import sqlite3


# создание БД
def create_sql_db():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users_mileage (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
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
                        date DATE,
                        day_mileage FLOAT
                    )
                    ''')
        # print("Создана таблица day_mileage")
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS week_mileage (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        week DATE,
                        week_mileage FLOAT
                    )
                    ''')
        # print("Создана таблица week_mileage")
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS month_mileage (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER,
                        month DATE,
                        month_mileage FLOAT
                    )
                    ''')
        # print("Создана таблица month_mileage")

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Есть БД. Соединение с SQLite закрыто")


# добавление нового юзера в таблицу users_mileage
def add_data_db(telegram_id: int, new_mileage: float):
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()

        # добавляем новую запись в таблицу users_mileage
        cursor.execute('''
            INSERT INTO users_mileage(
                        telegram_id,
                        day_mileage,
                        week_mileage,
                        month_mileage,
                        total_mileage)
                        VALUES (?, ?, ?, ?, ?)
                        ''',
                       (telegram_id,
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
def read_user_satistics_db(telegram_id):
    conn = sqlite3.connect('mileage.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT day_mileage, week_mileage, month_mileage, total_mileage FROM users_mileage 
                    WHERE telegram_id = ?''', (telegram_id,), )
    user_statistics = cursor.fetchone()
    return user_statistics


# запрос общей статистики
def read_all_statistics_db():
    conn = sqlite3.connect('mileage.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT
        ''')


def update_day_data_db(telegram_id: int, new_mileage: float):
    conn = sqlite3.connect('mileage.db')
    cursor = conn.cursor()

    # получаем текущие пробеги
    cursor.execute('''SELECT day_mileage, week_mileage, month_mileage, total_mileage FROM users_mileage
                        WHERE telegram_id = ?''', (telegram_id,), )

    # получаем результат запроса
    result_db = cursor.fetchone()
    # проверяем есть ли пользователь в БД
    if not result_db:
        add_data_db(telegram_id, new_mileage)
    else:
        # обновляем дневной пробег пользователя
        day_mileage, week_mileage, month_mileage, total_mileage = result_db
        day_mileage += new_mileage
        week_mileage += new_mileage
        month_mileage += new_mileage
        total_mileage += new_mileage

        cursor.execute('''
            UPDATE users_mileage SET 
                day_mileage = ?,
                week_mileage = ?,
                month_mileage = ?,
                total_mileage = ?
                WHERE 
                telegram_id = ?''',
                       (day_mileage,
                        week_mileage,
                        month_mileage,
                        total_mileage,
                        telegram_id))
        conn.commit()

        # закрываем соединение с базой данных
        conn.close()
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
            SELECT telegram_id,
            strftime('%d.%m.%Y', datetime('now')) as date,
            day_mileage
            FROM users_mileage
            ''')

        result_db = cursor.fetchall()

        sql_query = '''INSERT INTO day_mileage
                        (telegram_id , date, day_mileage)
                        VALUES (?, ?, ?)'''

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
        cursor.close()

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
                    SELECT telegram_id,
                    strftime('%W', datetime('now')) as date,
                    week_mileage
                    FROM users_mileage
                    ''')

        result_db = cursor.fetchall()

        sql_query = '''INSERT INTO week_mileage
                                (telegram_id , week, week_mileage)
                                VALUES (?, ?, ?)'''

        cursor.executemany(sql_query, result_db)
        conn.commit()
        print("Записи успешно вставлены в таблицу", cursor.rowcount)

        # удаляем недельную статистику в таблице users_mileage
        cursor.execute('''UPDATE users_mileage SET week_mileage = 0''')

        # сохраняем изменения в базе данных
        conn.commit()
        conn.close()
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
                    SELECT telegram_id,
                    strftime('%m', datetime('now')) as date,
                    month_mileage
                    FROM users_mileage
                    ''')

        result_db = cursor.fetchall()

        sql_query = '''INSERT INTO month_mileage
                                (telegram_id , month, month_mileage)
                                VALUES (?, ?, ?)'''

        cursor.executemany(sql_query, result_db)
        conn.commit()
        print("Записи успешно вставлены в таблицу", cursor.rowcount)

        # удаляем месячную статистику в таблице users_mileage
        cursor.execute('''UPDATE users_mileage SET month_mileage = 0''')

        # сохраняем изменения в базе данных
        conn.commit()
        conn.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")
