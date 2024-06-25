from datetime import datetime
from db import Database
import time
from datetime import date
def is_admin(info):
    if (info[3] == 1):
        return 1
    return 0

def add_spaces(str,space_count):
    return str + ' ' * space_count
def format_info_test(colums_info,users_info):
    if (len(users_info) == 0):
        return "Данных пока нет"
    answer = ""
    users_count = len(users_info)
    user_info_count = len(users_info[0])
    max_lens = []
    column_names = []
    for i in colums_info:
        column_name = i[0]
        max_lens.append(len(column_name))
        column_names.append(column_name)
    for i in range(0,users_count):
        for t in range(0,user_info_count):
            info_len = len(str(users_info[i][t]))
            if (info_len > max_lens[t]):
                max_lens[t] = info_len
    for i in range(0,user_info_count):
        answer += column_names[i]
        answer = add_spaces(answer,max_lens[i] - len(column_names[i]))
        answer += " | "
    answer += '\n'
    for i in range(0,users_count):
        for t in range(0,user_info_count):
            value = str(users_info[i][t])
            answer += value
            answer = add_spaces(answer,max_lens[t] - len(value))
            answer += " | "
        answer += '\n'
    return f"`{answer}`"
def format_info(colums_info,users_info):
    if (len(users_info) == 0):
        return "Данных пока нет"
    answer = ""
    users_count = len(users_info)
    user_info_count = len(users_info[0])
    max_lens = []
    column_names = []
    for i in colums_info:
        column_name = i[0]
        max_lens.append(len(column_name))
        column_names.append(column_name)
    for i in range(0,users_count):
        for t in range(0,user_info_count):
            info_len = len(str(users_info[i][t]))
            if (info_len > max_lens[t]):
                max_lens[t] = info_len
    for i in range(0,user_info_count):
        answer += column_names[i]
        answer = add_spaces(answer,max_lens[i] - len(column_names[i]))
        answer += " | "
    answer += '\n'
    for i in range(0,users_count):
        for t in range(0,user_info_count):
            value = str(users_info[i][t])
            answer += value
            answer = add_spaces(answer,max_lens[t] - len(value))
            answer += " | "
        answer += '\n'
    return f"<pre>{answer}</pre>"
def format_info_mobile(colums_info,users_info):
    if (len(users_info) == 0):
        return "Данных пока нет"
    answer = ""
    colums_len = len(users_info[0])
    for i in users_info:
        for t in range(0,colums_len):
            answer += f"{colums_info[t][0]}: {i[t]}\n"
        answer += "\n\n"
    return answer
def format_tasks_works(tasks, works):
    answer = ""
    answer += "Ваши задачи на сегодня:\n"
    count = 0
    if (len(tasks) != 0):
        for i in  tasks:
            count += 1
            answer += i[1] + '\n'
    if (len(works) != 0):
        for i in works:
            date = datetime.strptime(i[3],"%d-%m-%Y").date()
            date_today = date.today()
            if (date_today >= date):
                answer += i[1] + '\n'
                count += 1
    answer += "Нажмите на кнопку с наименованием задания если вы его выполнили:\n"
    if (count == 0):
        answer = "У вас сегодня нет дел! Отдыхайте"
    return answer

def is_valid_date(date_str):
    try:
        if (datetime.strptime(date_str, "%d-%m-%Y").date() >= date.today()):
            return True
        return False
    except ValueError:
        return False

def read_key(file_path):
    with open(file_path, 'r') as file:
        content = file.readline()
        return content.strip()


def send_notifications(db: Database,bot):
    last_time = datetime.now()
    tasks = db.get_all_task()
    works = db.get_all_work()
    for i in tasks:
        if (i[2] != None):
            telegram_id = db.get_telegram_id(i[2])
            bot.send_message(telegram_id, f"У вас есть задание '{i[1]}'!")
    for i in works:
        if (datetime.strptime(i[3], "%d-%m-%Y") <= last_time):
            if (i[2] != None):
                telegram_id = db.get_telegram_id(i[2])
                bot.send_message(telegram_id, f"У вас есть задание '{i[1]}'!")
    while (True):
        current_time = datetime.now()
        tasks = db.get_all_task()
        for i in tasks:
            if (i[2] != None):
                telegram_id = db.get_telegram_id(i[2])
                difference = (current_time - last_time).total_seconds()/60
                if (difference >= i[3]):
                        bot.send_message(telegram_id,f"У вас есть задание '{i[1]}'!")
                        last_time = current_time
        if (current_time.hour == 10 and current_time.minute < 10):
            works = db.get_all_work()
            for i in works:
                if (datetime.strptime(i[3],"%d-%m-%Y") <= current_time):
                    if (i[2] != None):
                        telegram_id = db.get_telegram_id(i[2])
                        bot.send_message(telegram_id,f"У вас есть задание '{i[1]}'!")
        time.sleep(5*60)

def format_question_answers(questions_info,answers_info):
    answer = ""
    for i in answers_info:
        for t in questions_info:
            if (t[0] == i[1]):
                answer += f"{t[1]}\nОтвет: {i[2]}\n\n"
    return answer


def format_quesions(questions_info):
    if (len(questions_info) == 0):
        return "В базе нет вопросов"
    answer = ""
    for i in questions_info:
        answer += f"id: {i[0]}\n{i[1]}\n\n"
    return answer

def notificate(user_ids,text,bot):
    for i in user_ids:
        bot.send_message(i,text)
