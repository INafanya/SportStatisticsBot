import sqlite3
from datetime import datetime, timedelta
from time import strftime

import aiosqlite as aiosqlite

def get_yesterday():
    date_format = '%d.%m.%Y'
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_format = yesterday.strftime(date_format)
    return yesterday_format

def get_today():
    date_format = '%d.%m.%Y'
    today = datetime.now()
    today_format = today.strftime(date_format)
    return today_format
def read_day_rating():
    '''
    1. Считать из БД кол-во человек в клубе
    2. Взять кол-во участников в минимальном клубе(минимум 1)
    3.
    :return:
    '''
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
    print(f"Минимальное кол-во парней: {min_club_count_man}")
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
    print(f"Минимальное кол-во девушек: {min_club_count_woman}")

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
    print(f"Суммарный пробег парней: {club_mileage_man}")
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
    print(f"Суммарный пробег девушек: {club_mileage_woman}")

    sql_query = '''INSERT INTO day_club_mileage (category, date, gender, mileage, active_users)
                                            VALUES (?, ?, ?, ?, ?)'''
    cursor.executemany(sql_query, club_mileage_man)
    conn.commit()
    cursor.executemany(sql_query, club_mileage_woman)
    conn.commit()
    # суммируем с предыдущими пробегами
    if conn:
        conn.close()
        return club_mileage_man, club_mileage_woman

        # async def select_all(par, part):
        #     async with aiosqlite.connect('db') as conn:
        #         cursor = await conn.execute("SELECT * FROM table WHERE a=b LIMIT %s OFFSET %s" % (par, part)
        #         row = await cursor.fetchall()
        #         return row

read_day_rating()

