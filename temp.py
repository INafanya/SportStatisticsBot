mileage_data = {}

def add_mileage_data(
        telegram_id: int,
        mileage: float
):
    if telegram_id in mileage_data:
        mileage_data[telegram_id] += mileage
    else:
        mileage_data[telegram_id] = mileage

add_mileage_data(telegram_id=12345, mileage=55)

print(mileage_data)

add_mileage_data(telegram_id=12345, mileage=55555)
print(mileage_data)
