import sqlite3

import sqlite3

# устанавливаем соединение с базой данных
conn = sqlite3.connect('mileage.db')

# создаем курсор для выполнения операций с базой данных
cursor = conn.cursor()

# задаем значения для новой записи
telegram_id = 11111
day_mileage = 5


# добавляем новую запись в таблицу users
cursor.execute('INSERT INTO users_mileage (telegram_id, day_mileage) VALUES (?, ?)', (telegram_id, day_mileage))

# сохраняем изменения в базе данных
conn.commit()

# закрываем соединение с базой данных
conn.close()