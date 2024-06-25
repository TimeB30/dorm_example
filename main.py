import telebot
from telebot import types
from db import Database
from func import *
from buttons import *
import threading
import sys
token = read_key("key.txt")
bot = telebot.TeleBot(token,num_threads=6)
db = Database("dbname=dbname user=user password=password host=host port=port")
if (db.connection_status == 0):
    print("Connection error")
    sys.exit(1)

user_input = {}

def check_input(user_id, text,bot, is_double = 0):
    answer = 0
    try:
        answer = int(text)
        if (answer < 0):
            bot.send_message(user_id, "Вы ввели отрицательное число, попробуйте снова")
            return -1
    except:
        bot.send_message(user_id, "Неправильный ввод, попробуйте снова")
        return -1
    if (is_double):
        if (answer != 1 and answer != 0):
            bot.send_message(user_id, "Неправильный ввод, попробуйте снова")
            return -1
    return answer
@bot.message_handler(commands = ["start", "help"])
def start(message: types.Message):
    user_id = message.from_user.id
    if (len(db.get_all_users_info()) == 0):
        bot.send_message(user_id,"Вы являетесь первым пользователем бота, поэтому вы станете администратором\nВведите фамилию и имя ",reply_markup=first_entry_menu)
        user_input[user_id] = [0,1]
        return
    user_info = db.get_user_info(user_id)
    if (user_info == None):
        bot.send_message(user_id,"Вас нет в данном блоке\nВведите свою фамилию и имя",reply_markup=first_entry_menu)
        user_input[user_id] = [0,0]
        return
    else:
        if (is_admin(user_info)):
            bot.send_message(user_id, "Вы администратор!", reply_markup=admin_menu)
        else:
            bot.send_message(user_id, "Дорбро пожаловать в наш блок!",reply_markup=user_menu)



@bot.message_handler(content_types=["text"])
def get_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    user_info = db.get_user_info(message.from_user.id)
    if (text == "отмена"):
        if (user_id in user_input):
            if (user_input[user_id][0] == 0):
                bot.send_message(user_id, "Действие отменено",reply_markup=first_entry_menu)
            elif (user_input[user_id][0] == 1):
                bot.send_message(user_id, "Действие отменено",reply_markup=user_menu)
            else:
                bot.send_message(user_id, "Действие отменено")
            user_data = user_input[user_id]
            try:
                bot.delete_message(user_id,user_data[1])

            except:
                try:
                    bot.delete_message(user_id,user_data[-1])
                except:
                    pass
            user_input.pop(user_id)
        else:
            bot.send_message(user_id, "У вас нет никаких взаимодействий")
        return
    if (user_id in user_input):
        input_data = user_input[user_id]
        if (input_data[0] == 0):  #sign up
            text_split = text.split()
            if (len(text_split) != 2):
                bot.send_message(user_id,"Вы ввели неправильное количество аргументов, попробуйте снова")
                return
            if (input_data[1] == 1):
                db.add_user(user_id,text_split[0],text_split[1],True)
                bot.send_message(user_id,"Вы добавлены",reply_markup=admin_menu)
                user_input.pop(user_id)
            else:
                db.add_user(user_id, text_split[0], text_split[1], False)
                question_data = db.get_question(1);
                if (question_data != None):
                    bot.send_message(user_id, "Вы добавлены, пройдтие опрос и администратор распределит ваши обязанности")
                    bot.send_message(user_id, question_data[1], reply_markup=make_test_buttons(question_data[2]))
                    user_input[user_id] = [1, 1,question_data[2],question_data[0]]
                else:
                    admins = db.get_admins()
                    notificate(admins, "Зарегистрировался новый пользователь", bot)
                    bot.send_message(user_id,
                                     "Добро пожаловать в блок! Ожидайте пока администратор распределит ваши обязанности")
                    user_input.pop(user_id)
        elif (input_data[0] == 1): #add answers
            answer = check_input(user_id,text,bot)
            if (answer != -1):
                if (answer > input_data[2] or answer == 0):
                    bot.send_message(user_id,"Вы ввели несуществующий вариант ответа")
                    return
                db.add_answer(user_id,input_data[3],answer)
            else:
                return
            input_data[1] = input_data[1] + 1
            question_data = db.get_question(input_data[1])
            if (question_data != None):
                bot.send_message(user_id,question_data[1],
                             reply_markup=make_test_buttons(question_data[2]))
                input_data[2] = question_data[2]
                input_data[3] = question_data[0]
            else:
                user_input.pop(user_id)
                admins = db.get_admins()
                notificate(admins,"Зарегистрировался новый пользователь",bot)
                bot.send_message(user_id,"Добро пожаловать в блок! Ожидайте пока администратор распределит ваши обязанности",reply_markup=user_menu)
        elif (input_data[0] == 2): #add question
            if (len(input_data) ==  2):
                answer = check_input(user_id,text,bot)
                if (answer != -1):
                    db.add_question(input_data[1],answer)
                    bot.send_message(user_id,"Вопрос добавлен")
                    user_input.pop(user_id)
            else:
                input_data.append(text)
                bot.send_message(user_id,"Введите количество ответов в вашем вопросе")
        elif (input_data[0] == 3): #delete question
            answer = check_input(user_id,text,bot)
            if (answer != -1):
                if (db.delete_question(answer) == 1):
                    bot.send_message(user_id,"Вопрос удален")
                    user_input.pop(user_id)
                else:
                    bot.send_message(user_id,"Вопрос не найден, попробуйте снова")
        elif (input_data[0] == 5): #add task
            if (len(input_data) == 1):
                input_data.append(text)
                bot.send_message(user_id, "Введите число минут между оповещениями, минимум 10")
            elif (len(input_data) == 2):
                answer = check_input(user_id,text,bot)
                if (answer != -1):
                    if (answer < 10):
                        bot.send_message(user_id,"Вы ввели число меньше 10, попробуйте снова")
                    else:
                        input_data.append(answer)
                        users_info = db.get_all_users_info()
                        message = bot.send_message(user_id, "Выберите пользователя который получит это задание",reply_markup=make_user_buttons(5,users_info).add(InlineKeyboardButton("Для всех",callback_data=f"{5}_all"),InlineKeyboardButton("Задать свободное задание",callback_data=f"{5}_free")))
                        input_data.append(message.message_id)
        elif (input_data[0] == 8): #add work
            if (len(input_data) == 1):
                bot.send_message(user_id,"Введите дату когда нужно будет приступить к работе в формате день-месяц-год")
                input_data.append(text)
            elif (len(input_data) == 2):
                if (is_valid_date(text)):
                    input_data.append(text)
                    bot.send_message(user_id, "Введите с какой периодичностью данное задание должно повторяться в днях")
                else:
                    bot.send_message(user_id, "Проверьте дату и введите снова")
            elif (len(input_data) == 3):
                answer = check_input(user_id,text,bot)
                if (answer != -1):
                    users_info = db.get_all_users_info()
                    message = bot.send_message(user_id, "Выберите пользователя который получить это задание",reply_markup=make_user_buttons(8,users_info).add(InlineKeyboardButton("Задать свободное задание",callback_data=f"{8}_free")))
                    input_data.append(answer)
                    input_data.append(message.message_id)
        return
    else:
        if (user_info == None):
            start(message)
            return
        if (text == "задания на сегодня"):
            tasks = db.get_user_tasks(user_id)
            works = db.get_user_works(user_id)
            bot.send_message(user_id, format_tasks_works(tasks, works), reply_markup=make_tasks_works_buttons(tasks, works))
        elif (text == "все задания"):
            message = bot.send_message(user_id, "Выберите с какого устройства была нажата кнопка",reply_markup=make_format_choice("t"))
            user_input[user_id] = [message.message_id]
            return
        elif (text == "все участники"):
            message = bot.send_message(user_id, "Выберите с какого устройства была нажата кнопка",reply_markup=make_format_choice("u"))
            user_input[user_id] = [message.message_id]
            return
        elif (text == "история заданий"):
            message = bot.send_message(user_id, "Выберите с какого устройства была нажата кнопка",
                             reply_markup=make_format_choice("d"))
            user_input[user_id] = [message.message_id]
        elif (text == "добавить задание"):
            user_input[user_id] = [5]
            bot.send_message(user_id, "Введите наименовние задания")
        elif (is_admin(user_info)):
            if (text == "добавить вопрос"):
                user_input[user_id] = [2]
                bot.send_message(user_id,"Введите вопрос")
            elif (text == "удалить вопрос"):
                questions = db.get_questions()
                message = bot.send_message(user_id,"Выберите вопрос для удаления",reply_markup=make_questions_button(3,questions))
                user_input[user_id] = [message.message_id]
            elif (text == "удалить участника"):
                if (user_id in user_input):
                    bot.delete_message(user_id,user_input[user_id][0])
                users_info = db.get_all_users_info()
                message = bot.send_message(user_id,"Выберите участника которого нужно удалить",reply_markup=make_user_buttons(4,users_info))
                user_input[user_id] = [message.message_id]
            elif (text == "передать задание"):
                tasks_info = db.get_all_task()
                if (len(tasks_info) == 0):
                    bot.send_message(user_id,"Заданий нет")
                else:
                    message = bot.send_message(user_id,"Выберите задание",reply_markup=make_all_tasks_buttons(6,tasks_info))
                    user_input[user_id] = [message.message_id]
            elif (text == "удалить задание"):
                tasks_info = db.get_all_task()
                message = bot.send_message(user_id,"Выберите задание для удаления",reply_markup=make_all_tasks_buttons(7,tasks_info))
                user_input[user_id] = [message.message_id]
            elif (text == "добавить работу"):
                user_input[user_id] = [8]
                bot.send_message(user_id, "Введите наименование работы")
            elif (text == "передать работу"):
                works_info = db.get_all_work()
                message = bot.send_message(user_id,"Выберите работу для передачи",reply_markup=make_all_works_buttons(9,works_info))
                user_input[user_id] = [message.message_id]
            elif (text == "удалить работу"):
                works_info = db.get_all_work()
                message = bot.send_message(user_id,"Выберите работу для удаления",reply_markup=make_all_works_buttons(10,works_info))
                user_input[user_id] = [message.message_id]
            elif (text == "изменить статус администратора"):
                users_info = db.get_all_users_info()
                message = bot.send_message(user_id,"Выберите пользователя",reply_markup=make_user_buttons(11,users_info))
                user_input[user_id] = [message.message_id]
            elif (text == "показать ответы"):
                users_info = db.get_all_users_info()
                message = bot.send_message(user_id,"Выберите чьи ответы нужно показать",reply_markup=make_user_buttons(12,users_info))
                user_input[user_id] = [message.message_id]
            elif (text == "показать вопросы"):
                questions = db.get_questions()
                bot.send_message(user_id,format_quesions(questions))
            return

@bot.callback_query_handler(func=lambda callback: callback.data)
def tasks_works_done(callback : types.CallbackQuery):
    user_id = callback.from_user.id
    callback_data = callback.data.split('_')
    func_num = callback_data[0]
    if (user_id in user_input):
        user_data = user_input[user_id]
        message_id = user_data[0]
        if (func_num == "1"):
            pass
        elif (func_num == "2"):
            pass
        elif (func_num == "3"):
            bot.delete_message(user_id,message_id)
            question_number = callback_data[1]
            db.delete_question(question_number)
            bot.send_message(user_id,"Вопрос удален")
            user_input.pop(user_id)
        elif (func_num == "4"):
            user_id_to_delete = callback_data[1]
            telegram_id = callback_data[4]
            bot.delete_message(user_id,message_id)
            bot.send_message(telegram_id,"Администатор удалил вас",reply_markup=first_entry_menu)
            db.delete_user(user_id_to_delete)
            bot.send_message(user_id,f"Пользователь {callback_data[2]} {callback_data[3]} удален")
            user_input.pop(user_id)
        elif (func_num == "5"):
            message_id = user_data[3]
            choice = callback_data[1]
            db.add_task(user_data[1],choice,user_data[2],user_id)
            bot.delete_message(user_id,message_id)
            bot.send_message(user_id,"Задание создано")
            if (choice == "all"):
                users = db.get_all_users_info()
                for i in users:
                    if (i[4] != user_id):
                        bot.send_message(i[4],"У вас есть новое задание")
            elif (choice != "free"):
                bot.send_message(callback_data[4],"У вас есть новое задание")
            user_input.pop(user_id)
        elif (func_num == "6"):
            task_id = callback_data[1]
            bot.delete_message(user_id,message_id)
            users_info = db.get_all_users_info()
            message = bot.send_message(user_id,"Выберите пользователя которому нужно передать задание", reply_markup=make_user_buttons(61,users_info).add(InlineKeyboardButton("Задать свободное задание",callback_data=f"{61}_free")))
            user_data[0] = message.message_id
            user_data.append(task_id)
        elif (func_num == "61"):
            bot.delete_message(user_id,message_id)
            user_id_to_set = callback_data[1]
            task_id = user_data[1]
            db.set_task(task_id,user_id_to_set)
            bot.send_message(user_id,"Операция выполнена")
            if (user_id_to_set != "free"):
                bot.send_message(callback_data[4],"У вас есть новое задание!")
            user_input.pop(user_id)
        elif (func_num == "7"):
            bot.delete_message(user_id,message_id)
            task_id = callback_data[1]
            db.delete_task(task_id)
            bot.send_message(user_id,"Задание удалено")
            user_input.pop(user_id)
        elif (func_num == "8"):
            message_id = user_data[4]
            user_id_to_set = callback_data[1]
            bot.delete_message(user_id,message_id)
            db.add_work(user_data[1],user_data[2],user_data[3],user_id_to_set)
            bot.send_message(user_id,"Работа создана")
            if (user_id_to_set != "free"):
                bot.send_message(callback_data[4],"У вас есть новая работа")
            user_input.pop(user_id)
        elif (func_num == "9"):
            work_id = callback_data[1]
            bot.delete_message(user_id,message_id)
            users_info = db.get_all_users_info()
            message = bot.send_message(user_id,"Выберите пользователя которому нужно передать работу", reply_markup=make_user_buttons(91,users_info).add(InlineKeyboardButton("Задать свободную работу",callback_data=f"{91}_free")))
            user_data[0] = message.message_id
            user_data.append(work_id)
        elif (func_num == "91"):
            bot.delete_message(user_id,message_id)
            user_id_to_set = callback_data[1]
            work_id = user_data[1]
            db.set_work(work_id, user_id_to_set)
            bot.send_message(user_id,"Работа задана")
            if (user_id_to_set != "free"):
                bot.send_message(callback_data[4],"У вас есть новая работа")
            user_input.pop(user_id)
        elif (func_num == "10"):
            bot.delete_message(user_id,message_id)
            work_id = callback_data[1]
            db.delete_work(work_id)
            bot.send_message(user_id,"Работа удалена")
            user_input.pop(user_id)
        elif (func_num == "11"):
            bot.delete_message(user_id,message_id)
            user_id_to_set = callback_data[1]
            telegram_id = callback_data[4]
            if (user_id_to_set == user_id):
                if (len(db.get_admins()) == 1):
                    bot.send_message(user_id,"Вы единственный администратор и не можете удалить этот статус, добавьте еще одного администратора")
                    user_input.pop(user_id)
                    return
            message = bot.send_message(user_id,f"Выберите опцию для пользователя: {callback_data[2]} {callback_data[3]}",reply_markup=yes_no_button(111,"Сделать администратором","Отобрать права администратора"))
            user_data[0] = message.message_id
            user_data.append(user_id_to_set)
            user_data.append(telegram_id)
        elif (func_num == "111"):
            bot.delete_message(user_id,message_id)
            user_id_to_set = user_data[1]
            status = callback_data[1]
            admin_status = db.get_user_info(user_data[2])[3]
            if (status == '1'  and admin_status == True):
                bot.send_message(user_id,"Пользователь уже администратор")
            elif(status == '0' and admin_status == False):
                bot.send_message(user_id,"Пользователь и так не является администартором")
            else:
                db.set_admin_status(user_id_to_set,status)
                bot.send_message(user_id, "Действие выполнено")
                if (status == "1"):
                    bot.send_message(user_data[2],"Вы теперь администратор",reply_markup=admin_menu)
                else:
                    bot.send_message(user_data[2], "У вас отобрали права администратора", reply_markup=user_menu)
            user_input.pop(user_id)
        elif (func_num == "12"):
            bot.delete_message(user_id,message_id)
            user_id_to_set = callback_data[1]
            user_name = callback_data[2]
            user_surname = callback_data[3]
            question_answers = db.get_answers(user_id_to_set)
            questions = db.get_questions()
            if (len(question_answers) > 0):
                bot.send_message(user_id,
                                 f"{user_name} {user_surname}: \n\n" + format_question_answers(questions, question_answers))
            else:
                bot.send_message(user_id, "У данного пользователя нет ответов на вопросы")
            user_input.pop(user_id)
        else:
            bot.delete_message(user_id,message_id)
            user_input.pop(user_id)
    callback_data_type = callback.data[0]
    if (callback.data[2] == "t"):
        tasks = db.get_all_task()
        colums_users = db.get_collums_info("users")
        colums_task = db.get_collums_info("tasks")
        colums_task += (colums_users[1],)
        colums_task += (colums_users[2],)
        works = db.get_all_work()
        colums_work = db.get_collums_info("works")
        colums_work += (colums_users[1],)
        colums_work +=(colums_users[1],)
        if (callback.data[0] == "m"):
            if (len(tasks) > 0):
                bot.send_message(user_id, format_info_mobile(colums_task, tasks))
            else:
                bot.send_message(user_id, "Первая таблица пуста")
            if (len(works) > 0):
                bot.send_message(user_id, format_info_mobile(colums_work, works))
            else:
                bot.send_message(user_id, "Вторая таблица пуста")
        else:
            if (len(tasks) > 0):
                bot.send_message(user_id, format_info(colums_task, tasks), parse_mode="HTML")
            else:
                bot.send_message(user_id, "Первая таблица пуста")
            if (len(works) > 0):
                bot.send_message(user_id, format_info(colums_work, works), parse_mode="HTML")
            else:
                bot.send_message(user_id, "Вторая таблица пуста")
    elif (callback.data[2] == "u"):
        users_info = db.get_all_users_info()
        colums_info = db.get_collums_info("users")
        if (callback.data[0] == "m"):
            bot.send_message(user_id, format_info_mobile(colums_info, users_info))
        else:
            bot.send_message(user_id, format_info(colums_info, users_info), parse_mode='HTML')
    elif (callback.data[2] == "d"):
        tasks_done = db.get_table("tasks_done")
        tasks_done_colums = db.get_collums_info("tasks_done")
        works_done = db.get_table("works_done")
        works_done_colums = db.get_collums_info("works_done")
        if (callback.data[0] == "m"):
            if (len(tasks_done) > 0):
                bot.send_message(user_id, format_info_mobile(tasks_done_colums, tasks_done))
            else:
                bot.send_message(user_id, "Первая таблица пуста")
            if (len(works_done) > 0):
                bot.send_message(user_id, format_info_mobile(works_done_colums, works_done))
            else:
                bot.send_message(user_id, "Вторая таблица пуста")
        else:
            if (len(tasks_done) > 0):
                bot.send_message(user_id, format_info(tasks_done_colums, tasks_done), parse_mode="HTML")
            else:
                bot.send_message(user_id, "Первая таблица пуста")
            if (len(works_done) > 0):
                bot.send_message(user_id, format_info(works_done_colums, works_done), parse_mode="HTML")
            else:
                bot.send_message(user_id, "Вторая таблица пуста")
    else:
        bot.delete_message(user_id,callback.message.message_id)
        callback_data_id = callback.data[2:]
        if (callback_data_type == 't'):
            if (db.check_user_task(callback_data_id,user_id)):
                if (db.check_for_all(callback_data_id)):
                    db.task_done(user_id,callback_data_id)

                else:
                    answer_info = db.task_done(user_id, callback_data_id)
                    new_user_id = answer_info[0]
                    current_user_name = answer_info[1]
                    current_user_surname = answer_info[2]
                    task_name = answer_info[3]
                    bot.send_message(new_user_id,
                                     f"Пользователь {current_user_name} {current_user_surname} выполнил задание '{task_name}' теперь очередь ваша")
                bot.send_message(user_id, "Задание выполнено")
            else:
                bot.send_message(user_id,"Вы уже сделали данное задание")
                return
        elif (callback_data_type == 'w'):
            if (db.check_user_work(callback_data_id,user_id)):
                answer_info = db.work_done(user_id,callback_data_id)
                bot.send_message(user_id, "Задание выполнено")
            else:
                bot.send_message(user_id, "Вы уже сделали данное задание")

if __name__ == "__main__":
    threading.Thread(target=send_notifications,args = (db,bot)).start()
    bot.infinity_polling()
