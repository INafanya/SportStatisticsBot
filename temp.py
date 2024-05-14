import sqlite3
from datetime import datetime, timedelta


def get_yesterday():
    date_format = '%d.%m.%Y'
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    yesterday_format = yesterday.strftime(date_format)
    return yesterday_format


def read_day_rating():
    try:
        conn = sqlite3.connect('mileage.db')
        cursor = conn.cursor()
        print("Подключение к SQLite успешно")
        yesterday = get_yesterday()
        cursor.execute('''
                    SELECT 
                    COUNT(telegram_id)
                    FROM day_mileage
                    WHERE date = ?
                    ''', (yesterday,), )

        users_sum = cursor.fetchall()

        if users_sum[0][0] <= 8:
            cursor.execute('''
                            SELECT 
                            telegram_id,
                            username,
                            day_mileage
                            FROM day_mileage
                            WHERE date = ?
                            ORDER BY day_mileage DESC
                            ''', (yesterday,), )

            result = [cursor.fetchall()]

        else:
            cursor.execute('''
                SELECT 
                telegram_id,
                username,
                day_mileage
                FROM day_mileage
                WHERE date = ?
                ORDER BY day_mileage DESC
                LIMIT 5
                ''', (yesterday,), )

            winners = cursor.fetchall()

            cursor.execute('''
                        SELECT 
                        telegram_id,
                        username,
                        day_mileage
                        FROM day_mileage
                        WHERE day_mileage > 0 AND date = ?
                        ORDER BY day_mileage ASC
                        LIMIT 3
                        ''', (yesterday,), )
            loosers = cursor.fetchall()

            # result = winners + loosers[::-1] + users_sum
            result = [winners, loosers[::-1], users_sum]
            # cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
            print("Соединение с SQLite закрыто")
        return result

print(read_day_rating())