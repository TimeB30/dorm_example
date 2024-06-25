from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from db import Database
from datetime import datetime

my_assigments = KeyboardButton("задания на сегодня")
all_assigments = KeyboardButton("все задания")
all_users_btn = KeyboardButton("все участники")
kick_user_btn = KeyboardButton("удалить участника")
add_task_btn = KeyboardButton("добавить задание")
add_work_btn = KeyboardButton("добавить работу")
add_question = KeyboardButton("добавить вопрос")
remove_question = KeyboardButton("удалить вопрос")
remove_task_btn = KeyboardButton("удалить задание")
remove_work_btn = KeyboardButton("удалить работу")
set_task_btn = KeyboardButton("передать задание")
set_work_btn = KeyboardButton("передать работу")
cancel_btn = KeyboardButton("отмена")
tasks_works_done = KeyboardButton("история заданий")
question_answers = KeyboardButton("показать ответы")
questions = KeyboardButton("показать вопросы")
admin_status = KeyboardButton("изменить статус администратора")
from_mobile = InlineKeyboardButton("С телефона",callback_data="m")
from_desktop = InlineKeyboardButton("C компьютера",callback_data='d')
def make_format_choice(query_type):
    format_choice = InlineKeyboardMarkup()
    format_choice.add(InlineKeyboardButton("С телефона",callback_data=f"m_{query_type}"))
    format_choice.add(InlineKeyboardButton("C компьютера", callback_data=f"d_{query_type}"))
    return format_choice
admin_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(my_assigments,all_assigments,
                                                     kick_user_btn,add_task_btn,add_question,remove_question,
                                                     remove_task_btn,remove_work_btn,set_task_btn,
                                                     cancel_btn,all_users_btn,add_work_btn,set_work_btn,question_answers,questions,admin_status,tasks_works_done)



user_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(my_assigments,all_assigments,all_users_btn,tasks_works_done,add_task_btn,cancel_btn)

first_entry_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(cancel_btn)
def make_test_buttons(answers_count):
    answer = ReplyKeyboardMarkup()
    for i in range(1,answers_count+1):
        answer.add(KeyboardButton(i))
    answer.add(cancel_btn)
    return answer

def make_tasks_works_buttons(tasks_info = None, works_info = None):
    tasks_works = InlineKeyboardMarkup(row_width=1)
    if (tasks_info != None):
        for i in tasks_info:
            tasks_works.add(InlineKeyboardButton(i[1],callback_data=f"t_{i[0]}"))
    if (works_info != None):
        for i in works_info:
            date = datetime.strptime(i[3], "%d-%m-%Y")
            date_today = datetime.now()
            if (date_today >= date):
                tasks_works.add(InlineKeyboardButton(i[1],callback_data=f"w_{i[0]}"))
    return tasks_works

def make_user_buttons(function_number,users_info):
    users = InlineKeyboardMarkup(row_width=1)
    for i in users_info:
        users.add(InlineKeyboardButton(f"{i[1]} {i[2]}",callback_data=f"{function_number}_{i[0]}_{i[1]}_{i[2]}_{i[4]}"))
    return users

def make_all_tasks_buttons(function_number,tasks_info):
    tasks = InlineKeyboardMarkup(row_width=1)
    for i in tasks_info:
        tasks.add(InlineKeyboardButton(f"{i[0]}) {i[1]}",callback_data=f"{function_number}_{i[0]}"))
    return tasks
def make_all_works_buttons(function_number,works_info):
    works = InlineKeyboardMarkup(row_width=1)
    for i in works_info:
        works.add(InlineKeyboardButton(f"{i[0]}) {i[1]}",callback_data=f"{function_number}_{i[0]}"))
    return works
def yes_no_button(function_number,yes_str,no_str):
    button = InlineKeyboardMarkup(row_width=1)
    button.add(InlineKeyboardButton(yes_str,callback_data=f"{function_number}_1"))
    button.add(InlineKeyboardButton(no_str,callback_data=f"{function_number}_0"))
    return button
def make_questions_button(function_number,questions_info):
    questions = InlineKeyboardMarkup(row_width=1)
    for i in questions_info:
        questions.add(InlineKeyboardButton(f"{i[0]}) {i[1]}",callback_data = f"{function_number}_{i[0]}"))
    return questions