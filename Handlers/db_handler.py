import sqlite3

def create_sql_db():
    conn = sqlite3.connect('../mileage.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE users_mileage
                	(id INTEGER PRIMARY KEY,
                	telegram_id INTEGER,
                	day_mileage INTEGER,
                	week_mileage INTEGER,
                	month_mileage INTEGER,
                	total_mileage INTEGER)''')
    conn.close()

