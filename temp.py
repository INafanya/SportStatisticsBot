import sqlite3
from Handlers.db_handler import read_day_rating


def cmd_day_rating_test():

    day_rating = read_day_rating()
    users_summ = day_rating[-1][0]
    text_answer = ""

    for (index, i) in enumerate(day_rating):
        if index == len(day_rating) -1 :
            break
        text_answer += f"{index+1}. {day_rating[index][1]} - {day_rating[index][2]} км.\n"

        #print(f"{index + 1}. {day_rating[index][1]} - {day_rating[index][2]} км.")
    print(text_answer)
    #print(len(day_rating))


cmd_day_rating_test()