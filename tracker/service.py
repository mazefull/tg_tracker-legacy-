import sqlite3 as sq
import json
import os


class database:
    def __init__(self, name=None):
        self.name = name

    def new_db(self, name=None):
        if not name:
            name = self.__new_db_request_name()
            print(f"BUILDING: {name}.db")
            # print(f"CHECKING: DBBrowserForSQLite")
            # os.system('winget install -e --id DBBrowserForSQLite.DBBrowserForSQLite')

        name += '.db'
        db = sq.connect(str(name))
        cur = db.cursor()
        config().write_config(var='db', data=f"{name}")
        database()._db_init()

    def check_have_db(self):
        if not config().get_config('db'):
            if input('BUILD NEW DB? (Y/N): ') == 'Y':
                self.new_db()
                return config().get_config('db')
            else:
                print('NO DB. You should init it first as database.new_db')
                quit()
        else:
            db = config().get_config('db')
            if os.path.exists(db):
                return db
            else:
                if input('NO DB. BUILD NEW DB? (Y/N): ') == 'Y':
                    self.new_db(name=db)
                    return config().get_config('db')
                else:
                    print('NO DB. You should init it first as database.new_db')
                    quit()


    def __new_db_request_name(self):
        name = input('ENTER NAME FOR DB: ')
        if not name:
            print('NO_NAME. EXIT')
        else:
            return name

    def _db_init(self):
        db = sq.connect(database().check_have_db())
        cur = db.cursor()
        try:
            cur.execute("CREATE TABLE IF NOT EXISTS task("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "dt varchar(20),"
                        "task_id varchar(12),"
                        "task_kid varchar(12),"
                        "task_usergroup varchar(12),"
                        "task_type varchar(12),"
                        "task_desc TEXT,"
                        "task_tittle TEXT,"
                        "user_on_task TEXT,"
                        "status_on_task TEXT,"
                        "task_project TEXT,"
                        "glob_status INTEGER,"
                        "task_priority TEXT,"
                        "task_dd TEXT,"
                        "dd_last_notify TEXT)")

            cur.execute("CREATE TABLE IF NOT EXISTS users("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "userid varchar(12),"
                        "username TEXT,"
                        "fname TEXT,"
                        "usergroup varchar(12),"
                        "usermode varchar(12))")

            cur.execute("CREATE TABLE IF NOT EXISTS actions("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "dt varchar(20),"
                        "action_id varchar(12),"
                        "task_id varchar(12),"
                        "assign_id varchar(12),"
                        "comment_id varchar(12),"
                        "status_set_id varchar(12),"
                        "is_assign INTEGER,"
                        "is_status_set INTEGER,"
                        "is_comment INTEGER,"
                        "action_by_user INTEGER)")

            cur.execute("CREATE TABLE IF NOT EXISTS comment("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "dt varchar(20),"
                        "action_id varchar(12),"
                        "comment_id varchar(12),"
                        "author TEXT,"
                        "caption TEXT,"
                        "reply_action_id varchar(12))")

            cur.execute("CREATE TABLE IF NOT EXISTS assign("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "dt varchar(20),"
                        "action_id varchar(12),"
                        "assign_id varchar(12),"
                        "assign_to INTEGER)")

            cur.execute("CREATE TABLE IF NOT EXISTS status("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "dt varchar(15),"
                        "action_id varchar(12),"
                        "status_set_id varchar(12),"
                        "status_set INTEGER)")

            cur.execute("CREATE TABLE IF NOT EXISTS params("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "last_timer varchar(15))")

            db.commit()

        except sq.OperationalError:
            print('ERR SQL SYNTAX')

        else:
            print(f'SUCCES DB DEPLOYED: {config().get_config("db")}')


class config:
    def __init__(self, data=None):
        self.data = data

    def build_config(self):
        os.system('echo "" >> tracker.json')

    def write_config(self, var, data):
        try:
            file = open('tracker.json', 'w')

        except FileNotFoundError:
            self.build_config()

        else:
            to_json = {f'{var}': data}
            file.write(json.dumps(to_json))

    def get_config(self, var):
        try:
            file = open('tracker.json', 'r')

        except FileNotFoundError:
            self.build_config()
            self.write_config(var, '')

        else:
            data = json.load(file)
            return data[var]


db = sq.connect(database().check_have_db())
cur = db.cursor()



def upd(table, collumn, collumn_value, find_collumn, find_value):
    try:
        quer = f'UPDATE {str(table)} SET {str(collumn)} = "{str(collumn_value)}" WHERE "{str(find_collumn)}" = "{str(find_value)}"'
        cur.execute(quer)
        db.commit()
        # print(f'Success updated, {table}.{find_collumn}({find_value}).{collumn} = {collumn_value}')
    except:
        print('[SQL] UPD ERROR')

def get_last_status_activity(task_id):
    data = cur.execute("SELECT status_set_id FROM actions WHERE task_id == '{key}' AND is_status_set = '1' ORDER BY dt DESC LIMIT 1".format(key=task_id)).fetchone()
    return data[0]

def get_status_by_said(said):
    data = cur.execute("SELECT status_set FROM status WHERE status_set_id == '{key}'".format(key=said)).fetchone()
    if not data:
        return None
    else:
        return data[0]

def get_task_primary_info(task_id):
    data = cur.execute("SELECT dt, task_kid, task_usergroup, task_type, task_desc, task_tittle FROM task WHERE task_id == '{key}'".format(key=task_id)).fetchone()
    if not data:
        return None
    else:
        return data

def get_task_comments_ids(task_id):
    data = cur.execute(
        "SELECT comment_id FROM actions WHERE task_id == '{key}' AND is_comment = '1' ORDER BY dt DESC".format(
            key=task_id)).fetchall()
    if not data:
        return None
    else:
        return data

def get_task_comment_data(comment_id):
    data = cur.execute(
        "SELECT dt, author, caption FROM comment WHERE comment_id == '{key}' ORDER BY dt DESC".format(
            key=comment_id)).fetchone()
    if not data:
        return None
    else:
        return data

async def user_id_list(chat_id):
    data = cur.execute("SELECT userid FROM users WHERE userid == '{key}'".format(
        key=chat_id)).fetchone()
    print(data)
    if not data:
        data1 = cur.execute("SELECT usergroup FROM users WHERE userid == '{key}'".format(
            key=chat_id)).fetchone()
        if not data1:
            return (None, None)
        else:
            return ('usergroup', chat_id)
    else:
        return ('user', chat_id)


async def is_user_exist(chat_id):
    data = cur.execute("SELECT userid FROM users WHERE userid == '{key}'".format(
        key=chat_id)).fetchone()

    if not data:
        return False
    else:
        return True

async def init_user(data):
    cur.execute((
                    "INSERT INTO users (userid, username, fname) VALUES (?, ?, ?)"),
                data)
    db.commit()

async def get_users_creds():
    data = cur.execute("SELECT userid, fname FROM users").fetchall()

    if not data:
        return None
    else:
        return data

async def get_groups():
    data = cur.execute("SELECT usergroup, usergroup FROM users").fetchall()
    if not data:
        return None
    else:
        return data


async def get_active_tasks(user_id):
    data = cur.execute("SELECT task_id, task_kid FROM task WHERE user_on_task == '{key}' AND glob_status is not 0".format(
        key=user_id)).fetchall()
    print(data)
    if not data:
        return None
    else:
        return data

def get_project_new_taskint(project):
    data = cur.execute("SELECT count(task_project) FROM task WHERE task_project == '{key}'".format(
        key=project)).fetchone()
    if not data:
        return 1
    else:
        return int(data[0])+1

def get_projects():
    data = cur.execute("SELECT task_project FROM task GROUP BY task_project").fetchall()
    if not data:
        return None
    else:
        if len(data) == 1:
            return data[0]
        else:
            arr = []
            for dat in data:
                arr.append(dat[0])
            return arr


async def prepare_get_post(task_id):
    data = await get_task_info(task_id)
    report = (f"<b>Идентификатор</b>: {data[2]}\n"
              f"<b>Клиент</b>: {data[1]}\n"
              f"<b>Создано</b>: {data[0][:19]}\n"
              f"<b>Подробное описание</b>:\n\n{data[3]}")


async def get_task_info(task_id):
    data = cur.execute(
        "SELECT dt, task_kid, task_project, task_tittle, task_desc, status_on_task, task_priority FROM tracker WHERE task_id == '{key}'".format(
            key=task_id)).fetchall()
    return data

async def get_tasks_dd():
    data = cur.execute("SELECT task_kid, task_dd, dd_last_notify, user_on_task FROM task WHERE task_dd IS NOT NULL AND glob_status = 1").fetchall()
    if not data:
        return None
    else:
        # if len(data) == 1:
        #     return data
        arr = []
        for dat in data:
            arr.append(dat)
        return arr

async def fix_last_notify(task_kid, last_notify):
    upd('task', 'dd_last_notify', last_notify, 'task_kid', task_kid)

async def get_last_timer(now):
    data = cur.execute("SELECT last_timer FROM params").fetchone()
    if not data:
        cur.execute("INSERT INTO params(last_timer) VALUES('{key}')".format(key=now))
        db.commit()
        return None
    else:
        return data[0]

def fix_last_timer(now):
    upd('params', 'last_timer', now, 'id', '1')