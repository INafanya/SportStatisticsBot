import sqlite3


def read_day_rating():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        print("Подключение к SQLite успешно")

        cursor.execute('''
                    SELECT 
                    COUNT(telegram_id)
                    FROM day_mileage
                    WHERE date == strftime('%d.%m.%Y', datetime('now'))
                    ''')

        users_sum = cursor.fetchall()

        cursor.execute('''
            SELECT 
            telegram_id,
            username,
            day_mileage
            FROM day_mileage
            WHERE date == strftime('%d.%m.%Y', datetime('now'))
            ORDER BY day_mileage DESC
            LIMIT 5
            ''')

        winners = cursor.fetchall()

        cursor.execute('''
                    SELECT 
                    telegram_id,
                    username,
                    day_mileage
                    FROM day_mileage
                    WHERE day_mileage > 0 and date == strftime('%d.%m.%Y', datetime('now'))
                    ORDER BY day_mileage ASC
                    LIMIT 3
                    ''')
        loosers = cursor.fetchall()

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")
        return winners + loosers[::-1] + users_sum

for i in read_day_rating():
    print(i)

