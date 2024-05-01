import sqlite3

telegram_id = 1060800091

conn = sqlite3.connect('mileage.db')
cursor = conn.cursor()

cursor.execute('''SELECT day_mileage, week_mileage, month_mileage, total_mileage FROM users_mileage
                    WHERE telegram_id = ?''', (telegram_id,),)

result = cursor.fetchone()

print(result)

day_mileage, week_mileage, month_mileage, total_mileage = result

day_mileage += 7
print(day_mileage,week_mileage,month_mileage,total_mileage)

conn.commit()
conn.close()

