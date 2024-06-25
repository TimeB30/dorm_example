import sqlite3
from datetime import datetime, timedelta
import psycopg2

class Database:

    def __init__(self, db_name):
        try:
            self.connect_info = db_name
            test_connection = psycopg2.connect(db_name)
            test_connection.close()
            self.connection_status = 1
            # self.connection = psycopg2.connect(user="postgres", host="127.0.0.1", password ="123", database = db_name)
        except:
            self.connection_status = 0
            test_connection.close()

    def add_user(self, telegram_id, user_name, user_surname, is_admin=False):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"INSERT INTO users (user_name, user_surname,is_admin,telegram_id) VALUES (%s,%s,%s,%s);",
                                    (user_name, user_surname, is_admin, telegram_id,))

    def get_user_id(self,telegram_id,cursor):
        cursor.execute("SELECT user_id FROM users WHERE telegram_id = %s",(telegram_id,))
        return cursor.fetchone()[0]
    def delete_user(self, user_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,));
                deleted_rows_count = cursor.rowcount
                return deleted_rows_count

    def get_user_info(self, telegram_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
                return cursor.fetchone()

    def set_admin_status(self, user_id, status=0):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET is_admin = %s WHERE user_id = %s", (status,user_id, ))

    def get_user_works(self, telegram_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id FROM users WHERE telegram_id = %s",(telegram_id,))
                user_id = cursor.fetchone()[0]
                cursor.execute("SELECT * FROM works WHERE user_id = %s", (user_id,))
                return cursor.fetchall()

    def get_user_tasks(self, telegram_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id FROM users WHERE telegram_id = %s", (telegram_id,))
                user_id = cursor.fetchone()[0]
                cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
                return cursor.fetchall()
    def get_question(self, question_num):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM questions")
                questions = cursor.fetchall()
                if (question_num > len(questions)):
                    return None
                else:
                    return questions[question_num-1]

    def get_questions(self):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM questions ORDER BY question_number")
                return cursor.fetchall()

    def add_question(self, question, answers_count):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO questions (question_text,answers_count) VALUES (%s,%s)",
                                    (question, answers_count))

    def delete_question(self, question_number):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM questions WHERE question_number = %s", (question_number,))
                return cursor.rowcount

    def add_answer(self, telegram_id, question_number, answer):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id FROM users WHERE telegram_id = %s",(telegram_id,))
                user_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO answers (user_id,question_number,answer) VALUES (%s,%s,%s)",
                                    (user_id, question_number, answer,))

    def work_done(self, telegram_id, work_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                user_id = self.get_user_id(telegram_id,cursor)
                current_time = datetime.now()
                cursor.execute("SELECT * FROM users WHERE user_id = %s ORDER BY user_id", (user_id,))
                user_info = cursor.fetchone()
                cursor.execute("SELECT * from works WHERE work_id = %s ORDER BY user_id", (work_id,))
                work_info = cursor.fetchone()
                work_name = work_info[1]
                work_cycle = work_info[4]
                next_time = (current_time + timedelta(days=work_cycle)).date().strftime("%d-%m-%Y")
                current_time = current_time.strftime("%H:%M:%S %d-%m-%Y")
                user_name = user_info[1]
                user_surname = user_info[2]
                cursor.execute("UPDATE works SET date = %s WHERE work_id =  %s", (next_time, work_id,))
                cursor.execute(
                    "INSERT INTO works_done (work_name, user_id, user_name, user_surname, date_time) VALUES (%s,%s,%s,%s,%s)",
                    (work_name, user_id, user_name, user_surname, current_time,))

    def task_done(self, telegram_id, task_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                user_id = self.get_user_id(telegram_id,cursor)
                answer = []
                current_time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                user_info = cursor.fetchone()
                cursor.execute("SELECT task_name FROM tasks WHERE task_id = %s", (task_id,))
                task_name = cursor.fetchone()[0]
                user_name = user_info[1]
                user_surname = user_info[2]
                new_user = user_info
                cursor.execute("SELECT * FROM users ORDER BY user_id")
                users = cursor.fetchall()
                users_count = len(users)
                for i in range(0, users_count):
                    if (users[i][4] == telegram_id):
                        if (i == users_count - 1):
                            new_user = users[0]
                        else:
                            new_user = users[i + 1]
                        break;

                cursor.execute("UPDATE tasks SET user_id = %s WHERE task_id = %s", (new_user[0], task_id,))
                cursor.execute(
                    "INSERT INTO tasks_done (user_id, user_name, user_surname, task_name, date_time) VALUES (%s,%s,%s,%s,%s)",
                    (user_id, user_name, user_surname,task_name, current_time,))
                answer.append(new_user[4])
                answer.append(user_name)
                answer.append(user_surname)
                answer.append(task_name)
                return answer

    def get_all_users_info(self,):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users ORDER BY user_id")
                return cursor.fetchall()
    def get_user_names_surnames(self):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_name, user_surname FROM users ORDER BY user_id")
                return cursor.fetchall()

    def get_collums_info(self, table_name):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position",(table_name,))
                return cursor.fetchall()
    def get_admins(self):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                answer = []
                cursor.execute(f"SELECT telegram_id FROM users WHERE is_admin = true")
                ids =  cursor.fetchall()
                if (len(ids) != 0):
                    for i in ids:
                        answer.append(i[0])
                    return answer
                return answer
    def add_task(self, task_name, user_id, notification_frequency,admin_id = 0):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                if (user_id == "all"):
                    cursor.execute("SELECT user_id FROM users WHERE telegram_id = %s",(admin_id,))
                    admin_id = cursor.fetchone()[0]
                    cursor.execute("SELECT user_id FROM users WHERE user_id != %s",(admin_id,))
                    user_ids = cursor.fetchall()
                    for i in user_ids:
                        cursor.execute("INSERT INTO tasks (task_name,user_id,notif_freq,for_all) VALUES (%s,%s,%s,%s)",(task_name,i[0],notification_frequency,True))
                    return 1
                elif (user_id == "free"):
                    cursor.execute("INSERT INTO tasks (task_name,notif_freq) VALUES (%s,%s)",
                                        (task_name, notification_frequency,))
                    return 1
                else:

                    cursor.execute("INSERT INTO tasks (task_name,user_id,notif_freq) VALUES (%s,%s,%s)",
                                        (task_name, user_id, notification_frequency,))
                    return 1


    def delete_task(self, task_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
                return cursor.rowcount
    def set_task(self, task_id, user_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                if (user_id == "free"):
                    cursor.execute("UPDATE tasks SET user_id = NULL WHERE task_id = %s", (task_id,))
                else:

                    cursor.execute("UPDATE tasks SET user_id = %s WHERE task_id = %s", (user_id, task_id,))
                    return 1


    def add_work(self, work_name, date, work_cycle, user_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                try:
                    if (user_id == "free"):
                        cursor.execute(
                            "INSERT INTO works (work_name, date, work_cycle) VALUES (%s,%s,%s)",
                            (work_name, date, work_cycle,))
                    else:
                        cursor.execute("INSERT INTO works (work_name, user_id, date, work_cycle) VALUES (%s,%s,%s,%s)",
                                            (work_name, user_id, date, work_cycle,))
                    return 1
                except:
                    return 0

    def set_work(self, work_id, user_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                if (user_id == "free"):
                    cursor.execute("UPDATE works SET user_id = NULL WHERE work_id = %s", (work_id,))
                else:
                    cursor.execute("UPDATE works SET user_id = %s WHERE work_id = %s", (user_id, work_id))


    def delete_work(self, work_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM works WHERE work_id = %s", (work_id,))
                return cursor.rowcount > 0

    def get_task(self, task_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
                result = cursor.fetchone()
                return result

    def get_work(self, workd_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM works WHERE work_id = %s", (workd_id,))
                result = cursor.fetchone()
                return result
    def get_user_id(self,telegram_id,cursor):
        cursor.execute("SELECT user_id FROM users WHERE telegram_id = %s",(telegram_id,))
        return cursor.fetchone()[0]
    def check_user_task(self, task_id,telegram_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                user_id = self.get_user_id(telegram_id,cursor)
                cursor.execute("SELECT * FROM tasks WHERE user_id = %s AND task_id = %s", (user_id, task_id,))
                if (cursor.fetchone() == None):
                    return 0
                return 1

    def check_user_work(self, work_id, telegram_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                user_id = self.get_user_id(telegram_id, cursor)
                cursor.execute("SELECT * FROM works WHERE user_id = %s AND work_id = %s", (user_id, work_id,))
                if (cursor.fetchone() == None):
                    return 0
                return 1

    def get_all_task(self):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT tasks.*, users.user_name, users.user_surname FROM tasks LEFT JOIN users ON tasks.user_id = users.user_id ORDER BY tasks.task_id")
                return cursor.fetchall()
    def get_all_work(self):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT works.*, users.user_name, users.user_surname FROM works LEFT JOIN users ON works.user_id = users.user_id ORDER BY works.work_id")
                return cursor.fetchall()
    def get_answers(self, user_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM answers WHERE user_id = %s", (user_id,))
                return cursor.fetchall()
    def check_for_all(self,task_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT for_all FROM tasks WHERE task_id = %s",(task_id,))
                result = cursor.fetchone()[0]
                return result

    def get_table(self,table_name):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table_name}")
                return cursor.fetchall()
    def get_telegram_id(self,user_id):
        with psycopg2.connect(self.connect_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT telegram_id FROM users WHERE user_id = %s",(user_id,))
                return cursor.fetchone()[0]