import datetime
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
                        "dd_last_notify TEXT,"
                        "intask_id TEXT)")

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

def usp(data):
    ds = tuple((data).replace('(', '').replace("'", "").replace(")", "").split(","))
    return ds


class notifys:
    def __init__(self, notify_id=None, notify_status=None):
        self.id = notify_id
        self.status = notify_status

    def get_buffer_data_by_id(self, id):
        data = cur.execute("SELECT dt, notify_id, issuer, to_user, caption, task, status FROM notify_buffer WHERE notify_id == '{key}'".format(key=id)).fetchone()
        print(data)
        if not data:
            return None
        else:
            return data

    def get_notify_buffer(self, status=None, all=False):
        """
        Используй флаг all в режиме True чтобы выгрузить весь буфер без фильтра по статусу
        Можно указать
        :param status:
        :param all:
        :return:
        """

        if all:
            if status is not None:
                print('[NOTIFY BUFFER] Фильтр статуса не может быть использован вместе с флагом %ALL% ')
                quit()
            else:
                data = cur.execute("SELECT notify_id, status FROM notify_buffer").fetchall()
        else:
            if status is None:
                status = 'AWAIT'
            data = cur.execute("SELECT notify_id, status FROM notify_buffer WHERE status == '{key}'".format(key=status)).fetchall()

        print(data)
        if not data:
            return None
        else:
            return data

    def update_by_id(self, id, status):
        upd('notify_buffer', 'status', status, 'notify_id', id)

    def clear_done(self):
        cur.execute("DELETE FROM notify_buffer WHERE status='DONE'")
        db.commit()

    def get_users_to_notify(self, task_id):
        assigner = taskdata().get_assigner_on_task(task_id=task_id)
        try:
            assigner0 = assigner[0]

        except:
            pass

        finally:
            if users().is_assigner_is_group(data=str(assigner0)):
                return users().get_users_by_group(usergroup=assigner0)
            else:
                if users().is_user_exist(user_id=assigner0):
                    return assigner
                else:
                    return users().get_default_usergroup_users()

    async def fix_last_notify(self, task_kid, last_notify):
        upd('task', 'dd_last_notify', last_notify, 'task_kid', task_kid)

    async def get_last_timer(self, now):
        data = cur.execute("SELECT last_timer FROM params").fetchone()
        if not data:
            cur.execute("INSERT INTO params(last_timer) VALUES('{key}')".format(key=now))
            db.commit()
            return None
        else:
            return data[0]

    def fix_last_timer(self, now):
        upd('params', 'last_timer', now, 'id', '1')


class taskdata:
    def __init__(self, task_id=None, comment_id=None, chat_id=None):
        self.task_id = task_id
        self.comment_id = comment_id
        self.chat_id = chat_id

    def get_primary_info(self, task_id):
        data = cur.execute(
            "SELECT dt, task_kid, task_usergroup, task_type, task_desc, task_tittle FROM task WHERE task_id == '{key}'".format(
                key=task_id)).fetchone()
        if not data:
            return None
        else:
            return data

    def get_assigner_on_task(self, task_id):
        if self.task_id is not None:
            task_id = self.task_id
        data = cur.execute("SELECT user_on_task FROM task WHERE task_id = '{key}'".format(key=task_id)).fetchone()
        if not data:
            return None
        else:
            return data

    async def get_active_tasks(self, user_id):
        data = cur.execute(
            "SELECT task_id, task_kid FROM task WHERE user_on_task == '{key}' AND glob_status is not 0".format(
                key=user_id)).fetchall()
        print(data)
        if not data:
            return None
        else:
            return data

    async def get_all_active_tasks(self):
        data = cur.execute(
            "SELECT task_id, task_kid FROM task WHERE glob_status is not 0").fetchall()
        print(data)
        if not data:
            return None
        else:
            return data

    def get_project_new_taskint(self, project):
        data = cur.execute("SELECT count(task_project) FROM task WHERE task_project == '{key}'".format(
            key=project)).fetchone()
        if not data:
            return 1
        else:
            return int(data[0]) + 1

    async def get_task_info(self, task_id):
        data = cur.execute(
            "SELECT dt, task_kid, task_project, task_tittle, task_desc, user_on_task, status_on_task, task_priority, intask_id FROM task WHERE task_id == '{key}'".format(
                key=task_id)).fetchall()
        if not data:
            data = cur.execute(
                "SELECT dt, task_kid, task_project, task_tittle, task_desc, user_on_task, status_on_task, task_priority, intask_id FROM task WHERE task_kid == '{key}'".format(
                    key=task_id)).fetchall()

        return data

    async def get_task_issuer(self, task_id):
        data = cur.execute("SELECT action_by_user FROM actions WHERE task_id=='{key}' ORDER BY dt ASC LIMIT 1".format(key=task_id)).fetchone()
        return data[0]

    async def get_tasks_dd(self):
        data = cur.execute(
            "SELECT task_kid, task_dd, dd_last_notify, user_on_task FROM task WHERE task_dd IS NOT NULL AND glob_status = 1").fetchall()
        if not data:
            return None
        else:
            # if len(data) == 1:
            #     return data
            arr = []
            for dat in data:
                arr.append(dat)
            return arr

    def get_projects(self):
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

    def get_sd_project(self, intask_id):
        data = cur.execute("SELECT project FROM sd WHERE intask_id = '{sd_id}'".format(sd_id=intask_id)).fetchone()
        if not data:
            return None
        else:
            try:
                data = data[0]
            except:
                pass
            return data

    def get_sd_datasheet(self, intask_id):
        data = cur.execute("SELECT sheet FROM sd WHERE intask_id = '{sd_id}'".format(sd_id=intask_id)).fetchone()
        if not data:
            return None
        else:
            try:
                data = data[0]
            except:
                pass
            return data

    def get_sd_target(self, intask_id):
        sd_= self.get_sd_datasheet(intask_id)
        data = cur.execute("SELECT target FROM '{sheet}' WHERE intask_id = '{sd_id}'".format(sheet=sd_, sd_id=intask_id)).fetchone()
        if not data:
            return None
        else:
            try:
                data = data[0]
            except:
                pass
            return data

    async def prepare_get_post(self, task_id):
        data = await taskdata().get_task_info(task_id)
        try:
            data = data[0]
        except:
            pass


        issuer = await taskdata().get_task_issuer(task_id)
        report = (f"<b>Идентификатор</b>: {data[1]}\n"
                  f"<b>Заголовок</b>: {data[3]}\n"
                  f"<b>Проект</b>: {data[2]}\n"
                  f"<b>Создатель</b>: {users().get_user_fname_by_id(issuer)}\n"
                  f"<b>Исполнитель</b>: {users().get_user_fname_by_id(data[5])}\n"
                  f"<b>Создано</b>: {data[0][:19]}\n"
                  f"<b>Статус</b>: {data[6]}\n"
                  f"<b>Приоритет</b>: {data[7]}\n\n"
                  f"<b>Подробное описание</b>:\n{data[4]}\n\n"
                  f"Для выхода нажми /cancel")
        intask_id = None

        if data[8] is not None:
            intask_id = data[8]

        return report, intask_id

    def get_last_status_activity(self, task_id):
        data = cur.execute(
            "SELECT status_set_id FROM actions WHERE task_id == '{key}' AND is_status_set = '1' ORDER BY dt DESC LIMIT 1".format(
                key=task_id)).fetchone()
        return data[0]

    def get_status_by_said(self, said):
        data = cur.execute("SELECT status_set FROM status WHERE status_set_id == '{key}'".format(key=said)).fetchone()
        if not data:
            return None
        else:
            return data[0]

    def get_task_kid_by_id(self, task_id):
        data = cur.execute("SELECT task_kid FROM task WHERE task_id == '{key}'".format(key=task_id)).fetchone()
        if not data:
            return None
        else:
            return data[0]


    class comments:
        """
        Класс используется для получения данных о комментариях по таску

        """
        def __init__(self, task_id=None, comment_id=None):
            self.task_id = task_id
            self.comment_id = comment_id

        def get_ids(self, task_id=None):
            """
            Выгружаем ids комментов по task_id
            :param task_id:
            :return:
            """
            if self.task_id is not None:
                task_id = self.task_id
            data = cur.execute(
                "SELECT comment_id FROM actions WHERE task_id == '{key}' AND is_comment = '1' ORDER BY dt DESC".format(
                    key=task_id)).fetchall()
            # print('CLASS get_ids')
            if not data:
                return None
            else:
                return data

        def get_data(self, comment_id=None):
            """
            Выгружаем датасет по comment_id

            :param comment_id:
            :return:
            """
            if self.comment_id is not None:
                comment_id = self.comment_id
            data = cur.execute(
                "SELECT dt, author, caption FROM comment WHERE comment_id == '{key}' ORDER BY dt DESC".format(
                    key=comment_id)).fetchone()
            # print('CLASS get_data')
            if not data:
                return None
            else:
                return data

        def prepare_comments_poster(self, task_id=None, debug=False):
            header = f"Комментарии по задаче {task_id}\n"
            try:
                ids = reversed(taskdata().comments(task_id=task_id).get_ids())

                def build_comment(dt, author, caption, ):
                    preset = (f"Cоздано: {dt}\n"
                              f"Автор: {users().get_user_fname_by_id(author)}\n"
                              f"{caption}\n"
                              f"-\n")
                    return preset
                if debug: print(f"IDS {ids}")
                com = f"{header}\n"
                for i in ids:

                    if debug:
                        print(f"IDS.I {i}")
                        com = com + f"{i[0]}\n" + build_comment(*(taskdata().comments().get_data(i[0])))
                    else:
                        com = com + build_comment(*(taskdata().comments().get_data(i[0])))
                return com
            except:
                return "Нет комментариев к задаче или возникла ошибка"

class users:
    def __init__(self, userdata=None, user_id=None, usergroup=None):
        self.user_id = user_id
        self.userdata = userdata
        self.usergroup = usergroup

    def get_users_by_group(self, usergroup):
        data = cur.execute("SELECT userid FROM users WHERE usergroup == '{key}'".format(key=usergroup)).fetchall()
        if not data:
            return None
        else:
            return data

    def get_usergroup(self, userid):
        data = cur.execute("SELECT usergroup FROM users WHERE userid == '{key}'".format(key=userid)).fetchall()
        if not data:
            return None
        else:
            try: data = data[0][0]
            except:
                print('ERROR FORMATTING USERGROUP. SC/459.service')
            return data


    def get_task_registation_request(self, userid):
        intask_id = cur.execute("SELECT intask_id FROM reg WHERE target == '{key}' ORDER BY dt DESC LIMIT 1".format(key=userid)).fetchone()
        print(intask_id)
        data = cur.execute("SELECT task_id, task_kid, user_on_task FROM task WHERE intask_id == '{key}'".format(key=intask_id[0])).fetchone()
        print(data)
        return data

    def is_assigner_is_group(self, data):
        ds = cur.execute("SELECT usergroup FROM users WHERE usergroup == '{key}'".format(key=data)).fetchone()
        if not ds:
            return False
        else:
            return True

    def is_user_exist(self, user_id):
        data = cur.execute("SELECT userid FROM users WHERE userid == '{key}'".format(
            key=user_id)).fetchone()

        if not data:
            return False
        else:
            return True

    async def get_default_usergroup_users(self):
        data = cur.execute("SELECT userid FROM users WHERE usermode == '{key}'".format(key='default')).fetchall()
        if not data:
            return None
        else:
            return data


    async def init_user(self, data):
        cur.execute((
                        "INSERT INTO users (userid, username, fname) VALUES (?, ?, ?)"),
                    data)
        db.commit()

    async def get_users_creds(self):
        data = cur.execute("SELECT userid, fname FROM users").fetchall()

        if not data:
            return None
        else:
            return data

    async def get_groups(self):
        data = cur.execute("SELECT usergroup, usergroup FROM users").fetchall()
        if not data:
            return None
        else:
            return data

    def get_user_fname_by_id(self, userid):
        data = cur.execute("SELECT fname, username FROM users WHERE userid == '{key}'".format(key=userid)).fetchone()
        if not data:
            return userid
        else:
            try:
                if data[1] is not None:
                    data = f"{data[0]} (@{data[1]})"
                else:
                    data = data[0]
            finally:
                return data

    def get_target_by_intask_id(self, intask_id):
        sheet = cur.execute("SELECT sheet FROM sd WHERE intask_id == '{intask_id}'".format(intask_id=intask_id)).fetchone()
        print("SHEET_0: ", sheet)
        target = cur.execute("SELECT target FROM '{sheet}' WHERE intask_id == '{intask_id}'".format(sheet=sheet, intask_id=intask_id)).fetchone()
        print("TARGET_01: ", target)
        if not target:
            return None
        else:
            return target

async def create_sd_sheet():
    cur.execute("CREATE TABLE IF NOT EXISTS sd("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "dt varchar(20),"
                "intask_id varchar(12),"
                "task_id varchar(12),"
                "project TEXT,"
                "sheet TEXT)")
    db.commit()


async def create_vpn_sheet():
    cur.execute("CREATE TABLE IF NOT EXISTS vpn("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "dt varchar(20),"
                "intask_id varchar(12),"
                "target TEXT,"
                "issuer TEXT,"
                "requestor TEXT,"
                "status_profile TEXT)")
    db.commit()


async def create_reg_sheet():
    cur.execute("CREATE TABLE IF NOT EXISTS reg("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "dt varchar(20),"
                "intask_id varchar(12),"
                "target TEXT,"
                "issuer TEXT,"
                "requestor TEXT,"
                "status_profile TEXT)")
    db.commit()


global permission_cash
permission_cash = {}


def permissions_cash_add(key, data):
    permission_cash[key] = data
    print(f'PERM_CASH: {datetime.datetime.now()} — | {key} —>> {permission_cash}')


class permit():





    permissions = {
        "main_menu": {
            "search": ("ALL_SERVICES_ACC", "pc_superuser", "ALL_NO_USR_ACC", "DEFAULT_SEARCH_ALLOW"),
            "informer": ("ALL_SERVICES_ACC", "ALL_NO_USR_ACC", "DEFAULT_INFORMER_ALLOW")
        },
        "task_menu_main": {
            "status": ("ALL_SERVICES_ACC", "ALL_NO_USR_ACC"),
            "assign": ("ALL_SERVICES_ACC", "ALL_NO_USR_ACC"),
            "comment": ("ALL_SERVICES_ACC", "ALL_NO_USR_ACC")
        }


    }


    permisson_chart = {
        "pc_default_run": ("TR_SERVICE_RUN",),
        "pc_default_light": ("pc_default_run", "TR_ISSUE_ALLOW"),
        "pc_default": ("pc_default_light", "TR_SELF_TASK_SPECTATE", "TR_SELF_ASSIGNED_ACTION", "TR_TASK_ANY_TRANSFER_DENY"),
        "pc_default_team": ("pc_default", "TR_TEAM_TASK_WORKING"), #MUST TEAM ROLE! MUST TEAM_ID!
        "pc_default_team_opr": ("pc_default_team", "TR_TEAM_TASK_ADMIN"), #MUST TEAM_OPR ROLE! MUST TEAM_ID!
        "pc_default_team_adm": ("pc_default_team", "pc_spc_team_yoda"),  # MUST TEAM_ADM ROLE! MUST TEAM_ID!
        "pc_spc_usr_adm": ("TR_USER_ALL_MASTER",),
        "pc_spc_usr_team_adm":  ("TR_USER_TEAM_MASTER",), #MUST TEAM ROLE! MUST TEAM_ID!
        "pc_spc_team_yoda": ("pc_spc_usr_team_adm", "TR_TEAM_TASK_ADMIN"),  # MUST TEAM_ADM ROLE! MUST TEAM_ID!
        "pc_spc_project_yoda": "",
        "pc_superuser": ("ALL_SERVICES_ACC", "ALL_NO_LIMIT"),
        "pc_admin": ("ALL_SERVICES_ACC", "TR_USER_MANAGE_DENY"),


    }

    #TR_MASTER_TRANSFER_TO_TEAM_ALLOW


    def pc_role_find_in_list(self, req_role, user):
        """
        ДЕЛАЕМ ПЕРЕБОР РОЛЕЙ, ПОКА НЕ БУДЕТ НАЙДЕНА НУЖНАЯ
        СОБИРАЕМ СТАТИСТИКУ САМЫХ ПОПУЛЯРНЫХ РОЛЕЙ И РЕАЛИЗОВЫВАЕМ КЭШ ДЛЯ БЫСТРОЙ РАБОТЫ С РОЛЯМИ
        :param req_role:
        :return:
        """
        pms = []
        permissions = self.get_permissions_by_user(userid=user)
        for pm in permissions:
            pms = self.pc_role_unpacker(pm)

    def pc_role_dedouble(self, xcd):
        pass

    def pc_role_refactor(self, xc, xcr=None):
        pass


    def pc_role_unpacker_dc(self, dcs, pre_data=None, i=0, rr=None):
        permission_list = []
        permission_list_depends = []
        pc_main_roles = list(self.permisson_chart.keys())
        for dc in dcs:
            dc_data = self.permisson_chart[dc]
            print(f"DC= {dc}, DC_DATA= {dc_data}")
            for _dc_data in  dc_data:
                if str(_dc_data).startswith("pc_"):
                    if _dc_data in pc_main_roles:
                        permission_list_depends.append(_dc_data)
                    else:
                        pass
                else:
                    permission_list.append(_dc_data)
        if rr is not None:
            if rr in permission_list:
                return True

        if pre_data is not None:
            for pre in pre_data:
                permission_list.append(pre)

        if permission_list_depends !=[]:
            return self.pc_role_unpacker_dc(dcs=permission_list_depends, pre_data=permission_list, i=i + 1)
        else:
            print(f'\nITER: — {i}\nXC: {permission_list}\nXC_ROLES: {permission_list_depends}')
            return permission_list



    def pc_role_unpacker(self, req_role):
        pc_main_roles = list(self.permisson_chart.keys())
        role_data = self.permisson_chart[req_role]
        dcs = []
        for rc in role_data:
            if rc in pc_main_roles:
                dcs.append(rc)
        permissions_cash_add(key=req_role, data=self.pc_role_unpacker_dc(dcs))


    def get_permissions_by_user(self, userid):
        master_permission = cur.execute("SELECT master_permission FROM users WHERE userid == '{key}'".format(key=userid)).fetchone()
        project_permissions = ""
        special_permissions = ""
        try:
            master_permission = master_permission[0]
        except:
            master_permission = master_permission


        return (master_permission, project_permissions, special_permissions)


    def buttons_menu_permissions(self, userid):
        pass

    def main_menu_btns(self, userid):
        bts = {
            '00': "main_menu_tasks_no_na",
            '01': "main_menu_tasks_no_search",
            '10': "main_menu_tasks_no_informer",
            '11': "main_menu_tasks",
        }


        permissions = self.get_permissions_by_user(userid)
        print(f'PM_CHART = {permissions}')
        alltasks_permits = self.permissions["main_menu"]["search"]
        informer_permits = self.permissions["main_menu"]["informer"]
        # print(permissions)
        # print(alltasks_permits)
        # print(informer_permits)

        main_ds = ""
        if [item for item in permissions if item in alltasks_permits]:
            main_ds = "1"
        else:
            main_ds = "0"

        if [item for item in permissions if item in informer_permits]:
            main_ds = main_ds + "1"
        else:
            main_ds = main_ds + "0"



        # print(main_ds)
        button = bts[main_ds]
        print(main_ds)
        return button




    def get_main_permission(self, userid):
        pass

    def project_permission(self, userid, project):
        pass

    def set_user_usergroup(self, userid, usergroup):
        upd(table='users', collumn='usergroup', collumn_value=usergroup, find_collumn='userid', find_value=userid)
        permit().set_user_master_permission(userid, usergroup)
        chck = users().get_usergroup(userid=userid)
        if chck == userid:
            return True
        else:
            print("CHUCK: ", chck)
            return chck

    def set_user_master_permission(self, userid, usergroup):
        fast_roles = {
            "default": "DEFAULT_NO_SEARCH",
            "admin": "ALL_SERVICES_ACC"
        }
        try:
            mp = fast_roles[usergroup]
            try:
                upd(table='users', collumn='master_permission', collumn_value=mp, find_collumn='userid', find_value=userid)
            except:
                print(
                    f'Ошибка при назначении: master_permission ${usergroup} для {users().get_user_fname_by_id(userid)}\n'
                    f'Не найден пользователь {userid} в БД')

        except:
            print(f'Ошибка при назначении: master_permission ${usergroup} для {users().get_user_fname_by_id(userid)}\n'
                  f'Не найден ключ для роли {usergroup} в базе $fast_roles')

    def set_user_project_permission(self, user, project, permission=None, permission_group=None):
        pass

    def is_main_permit_grant_project_role(self, userid, project):
        pass

    def is_main_permit_reject_project_access(self, userid, project):
        pass