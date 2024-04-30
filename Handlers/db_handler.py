import sqlite3

# создание БД
def create_sql_db():
    # создаем соединение с БД
    conn = sqlite3.connect('mileage.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE users_mileage
                	(id INTEGER PRIMARY KEY, telegram_id INTEGER, day_mileage FLOAT, week_mileage FLOAT, month_mileage FLOAT, total_mileage FLOAT)''')
    conn.close()

def add_data_db(telegram_id: int, new_mileage: float):
    conn = sqlite3.connect('mileage.db')
    cursor = conn.cursor()

    # добавляем новую запись в таблицу users_mileage
    cursor.execute('''INSERT INTO users_mileage(
                    telegram_id, day_mileage, week_mileage, month_mileage, total_mileage) VALUES (?, ?, ?, ?, ?)''',
                   (telegram_id, new_mileage, new_mileage, new_mileage, new_mileage))

    # сохраняем изменения в базе данных
    conn.commit()
    conn.close()

# запрос статистики по пользователю
def read_user_satistics_db(telegram_id):
    conn = sqlite3.connect('mileage.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT
    ''')

# запрос общей статистики
def read_all_statistics_db():
    conn = sqlite3.connect('mileage.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT
        ''')


def update_day_data_db(telegram_id: int, new_mileage: float):
    conn = sqlite3.connect('mileage.db')
    cursor = conn.cursor()

    # получаем текущий дневной пробег
    cursor.execute('''SELECT day_mileage FROM users_mileage
                    WHERE telegram_id=?''', (telegram_id,),)

    # получаем результат запроса
    day_mileage_db = float(cursor.fetchone()[0])

    # проверяем есть ли пользователь в БД
    if not day_mileage_db:
        add_data_db(telegram_id, new_mileage)
    else:
        # обновляем дневной пробег пользователя
        day_mileage = day_mileage_db + new_mileage
        cursor.execute('''UPDATE users_mileage SET day_mileage = ?
                       WHERE telegram_id = ?''', (day_mileage, telegram_id))
        conn.commit()

        # закрываем соединение с базой данных
        conn.close()
        return day_mileage