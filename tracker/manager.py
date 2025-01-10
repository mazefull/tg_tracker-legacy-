import asyncio

from tracker.service import db, cur, upd, taskdata
from uuid import uuid4
from datetime import datetime as dt

class Permissions:

    permissions = {
        "usergroup": {
            "owner": "ALL_SERVICES_ACC",
            "admin": "ALL_NO_USR_ACC",
            "operator": "DEFAULT_ACC",
            "operator_nc": "DEFAULT_NO_SEARCH",
            "iss_user": "ONLY_ISSUE"
            ""
        },
        "project_roles": {
            "STARCON": {
                "admin": "STARCON_ADMIN_ACC",
                "admin_no_full": "STARCON_ADMIN_NO_SPECIAL",
                "operator": "STARCON_OPER",
                "issuer": "STARCON_ISSUER"
            }
        },
        "starcon_perms": {
            "admin": {
                "permission_group": "STARCON_ADMIN",
                "desc": "Полный доступ к старкону со спец задачами",
                "permissions": ("PROJECT_STARCON_FULL", "PROJECT_ONLY_STARCON", "PROJECT_STARCON_ADM_NC_ASSIGN_ALLOW")
            },
            "admin_nc": {
                "permission_group": "STARCON_ADMIN_NO_SPEC",
                "desc": "Админ доступ к старкону",
                "permissions": ("PROJECT_STARCON_FULL_NC", "PROJECT_ONLY_STARCON", "USERS_STARCON_VIEW_ONLY", "USERS_ONLY_STARCON_ASSIGNED")
            },
            "operator": {
                "permission_group": "STARCON_OPERATOR",
                "desc": "Создание, комментирование, переназначение своих задач, смена статуса",
                "permissions": ("PROJECT_ONLY_STARCON", "USERS_ONLY_STARCON_ASSIGNED", "PROJECT_ONLY_STARCON_ADM_ASSIGN")
            },

            "minimum": {
                "permission_group": "STARCON_ISSUER",
                "desc": "Только заведение задач проекта старкон",
                "permissions": ("PROJECT_ONLY_STARCON_ADM_ASSIGN", "TASK_REASSIGN_DENY")

            }



        }



    }


    def set_user_permisson(self):
        pass


class Task:
    presets = {
        "NewTask": {
            "status": {
                "status_set_id": str(uuid4())[-12:],
                "status_set": "NEW"
            },
            "assign": {
                'assign_id': str(uuid4())[-12:],
                'assign_to': ''
            }
        },
        None: {
            "status": {
                "status_set_id": str(uuid4())[-12:],
                "status_set": ""
            },
            "assign": {
                'assign_id': str(uuid4())[-12:],
                'assign_to': ''
            }
        }
    }

    build_presets = {
        "status": {
            "status_set_id": str(uuid4())[-12:],
            "status_set": ""
        },
        "assign": {
            'assign_id': str(uuid4())[-12:],
            'assign_to': ""
        },
        "comment": {
            "comment_id": str(uuid4())[-12:],  # DEPRECATED FUNC
            "author": "",
            "caption": "",
            "reply_action_id": "",
        }
    }

    build_sd = {
        "VPNREQ": {
            "sheet_presets": {
                "intask_id": str(uuid4())[-12:],
                "target": "",
                "issuer": "",
                "requestor": "",
                "status_profile": "REQUEST",
            },
            "sd_linker": {
                "intask_id": "",
                "task_id": "",
                "project": "VPNREQ",
                "sheet": "vpn"
            },
            "BP" : {
                1 : "REQUEST",
                2 : ("IN WORK", "DELAYED", "WAIT FOR INFO"),
                3 : ("APPROVE", "REJECT"),
                4 : "CLOSED"
            }
        }
    }

    root_statuses = {
        0: ('TRASHED', 'CLOSED', 'REJECTED', 'DONE'),
        1: ('DELAYED', 'WORK', 'BACKLOG', 'OPERATIONAL', 'WAIT FOR INFO')
    }

    def __init__(self, task_id=None, issuer_id=None, comment=None, status=None, assign=None, project=None, tittle=None, desc=None, from_sd = False):
        self.task_id = task_id
        self.issuer_id = issuer_id
        self.comment = comment
        self.status_to = status
        self.assign = assign
        self.project = project
        self.tittle = tittle
        self.desc = desc


    def new_issue(self, tittle, desc, deadline, project=None, priority=None, assign=None, user=None, intask_id=None, use_sd= False, from_sd = False, task_type='TRV'):
        taskid = str(uuid4())[-12:]
        print(f"TSKMNGER: {taskid}")
        task_usergroup = None

        if user is None:
            user = "system"


        if type(assign) is not str and type(assign) is not int:
            task_usergroup = assign[1]
            assign = assign[0]
        else:
            assign = assign

        task = {
            "task_id": taskid,
            "task_usergroup": task_usergroup,
        }

        data = Task()._build_action(desc=desc, taskid=taskid, tittle=tittle, assign=assign, project=project,
                                 priority=priority, user=user, mode="NewTask")
        print(f"TSKMNGER: {task}")
        print(f"TSKMNGER: {data}")
        task_project = data['data']['task']['project']
        #intask_id=intask_id

        if use_sd:
            sd_template_data = Task().build_sd[project]
            main_sheet = sd_template_data["sheet_presets"]
            sd_linker = sd_template_data["sd_linker"]



        task_transaction_data = [ts(), task["task_id"], task["task_usergroup"], task_type, task_project, desc, tittle, assign, 'NEW', 1, priority, deadline, intask_id]
        Task()._send(data, task_transaction_data)
        # Task()._run_task((ts(), task["task_id"], task["task_usergroup"], task_type, task_project, desc, tittle, assign, 'NEW', 1, priority))
        return Task().get_task_kid_by_id(task_id=taskid)




    def _build_sd_data(self):
        pass


    def _build_sd_linker_data(self):
        pass


    def sd_status_action(self, intask_id, status):
        datasheet = taskdata().get_sd_datasheet(intask_id)
        upd(table=datasheet, collumn='status_profile', collumn_value=status, find_collumn='intask_id', find_value=intask_id)



    def new_sd(self, intask_id, target, requestor, sheet, status_profile=None, issuer=None):
        if target == requestor:
            issuer = requestor
        sd_data = (ts(), intask_id, target, issuer, requestor, status_profile)
        print('SDMNGER.VPN: ', sd_data)
        cur.execute(("INSERT INTO '{sheett}' (dt, intask_id, target, issuer, requestor, status_profile) VALUES (?, ?, ?, ?, ?, ?)").format(sheett=sheet), sd_data)
        db.commit()


    def sd_task_worker(self, intask_id, task_id, project, sheet):
        sd_worker_data = (ts(), intask_id, task_id, project, sheet)
        cur.execute((
            "INSERT INTO sd (dt, intask_id, task_id, project, sheet) VALUES (?, ?, ?, ?, ?)"),
            sd_worker_data)
        db.commit()

    def tid_check(self, task_id):
        task_id = Task().is_task_exist(task_id)
        if task_id is None:
            quit(code='TASK NOT FOUND')
        return task_id


    def new_comment(self, author, caption, task_id, reply_action_id=None):
        task_id = Task().tid_check(task_id)
        action = Task()._build_action(taskid=task_id, comment=caption, user=author, reply_action_id=reply_action_id)
        Task()._send(action)

    def new_assign(self, task_id, assign_to):
        task_id = Task().tid_check(task_id)
        action = Task()._build_action(taskid=task_id, assign=assign_to)
        Task()._send(action)

    def new_status(self, task_id, status_set):
        task_id = Task().tid_check(task_id)
        action = Task()._build_action(taskid=task_id, status=status_set)
        Task()._send(action)


    def multi_action(self, task_id, user_id=None, assign_to=None, comment=None, status_to=None):
        task_id = Task().tid_check(task_id)
        action = Task()._build_action(taskid=task_id, user=user_id, assign=assign_to, comment=comment, status=status_to)
        Task()._send(action)


    def _build_action(self, taskid: str, assign=None,
                     comment=None, status=None, project=None,
                     priority=None, user=None, mode=None, tittle=None, desc=None, reply_action_id=None):
        """
        Собираем JSON активности трекера


        :param mode: Режим сборки
        :param desc: Описание задачи
        :param tittle: Заголовок задачи
        :param assign: Исполнитель задачи
        :param comment: Комментарий к задаче
        :param status: Статус задачи
        :param project: Проект задачи
        :param priority: Приоритет задачи
        :return: JSON
        """

        if project is None:
            project = "COM"
        if not priority:
            priority = 'Trivial'

        assign_to_json = Task()._build_assign(data=mode, assign=assign)
        status_to_json = Task()._build_status(data=mode, status=status)
        comment_to_json = Task()._build_comment(author=user, caption=comment, reply_action_id=reply_action_id)

        if user is None:
            user = 'system'

        to_json = {
            "setup": {
                "is_status_set": Task()._check_none(status_to_json),
                "is_assign": Task()._check_none(assign_to_json),
                "is_comment": Task()._check_none(comment_to_json)
            },
            "data": {
                "action_id": str(uuid4())[-12:],
                "action_by_user": user,
                "task": {
                    "task_id": taskid,
                    "project": project,
                    "tittle": tittle,
                    "priority": priority,
                    "desc": desc
                },
                "assign": assign_to_json,
                "comment": comment_to_json,
                "status": status_to_json,
            }
        }
        return to_json

    def _build_status(self, data, status=None):
        sample = ""
        try:
            sample = Task().presets[data]['status']
        except:
            pass

        else:
            if sample["status_set"] == '':
                if status is None:
                    sample = None
                else:
                    sample = Task().build_presets['status']
                    sample["status_set_id"] = str(uuid4())[-12:]
                    sample["status_set"] = status

            return sample

    def _build_assign(self, data, assign=None):
        sample = ""
        try:
            sample = Task().presets[data]['assign']

        except:
            pass

        else:
            if sample["assign_to"] == '':
                if assign is None:
                    if data == "NewTask":
                        sample["assign_to"] = 'admin'
                    else:
                        sample = None
                else:
                    sample = Task().build_presets['assign']
                    sample["assign_id"] = str(uuid4())[-12:]
                    sample["assign_to"] = assign

            return sample

    def _build_comment(self, author, caption, reply_action_id):
        sample = ""
        if not author:
            author = 'system'

        if not caption:
            return None

        else:
            sample = Task().build_presets['comment']
            sample["comment_id"] = str(uuid4())[-12:]
            sample["author"] = author
            sample["caption"] = caption
            if reply_action_id is not None:
                sample["reply_action_id"] = reply_action_id
            else:
                pass

        return sample

    def _check_none(self, data):
        if data is None:
            return 0
        else:
            return 1

    def _send(self, data, task_transaction_data=None):
        datachart = data['data']
        try:
            assign_id = datachart["assign"]["assign_id"]
        except:
            assign_id = None

        try:
            comment_id = datachart["comment"]["comment_id"]
        except:
            comment_id = None

        try:
            status_set_id = datachart["status"]["status_set_id"]
        except:
            status_set_id = None

        data_action = (ts(),
                       data['data']['action_id'],
                       data['data']['task']['task_id'],
                       assign_id,
                       comment_id,
                       status_set_id,
                       data['setup']['is_status_set'],
                       data['setup']['is_assign'],
                       data['setup']['is_comment'],
                       data['data']['action_by_user'])
        # Task().run_action(data_action)


        if data['setup']['is_comment'] == 1:
            data_comment = (
                ts(),
                data['data']['action_id'],
                comment_id,
                data['data']['comment']['author'],
                data['data']['comment']['caption'],
                data['data']['comment']['reply_action_id'])
        else:
            data_comment = None
            # Task().run_comment(data_comment)

        if data['setup']['is_status_set'] == 1:
            data_status = (
                ts(),
                data['data']['action_id'],
                status_set_id,
                data['data']['status']['status_set'])
            # Task().run_status(data_status)
        else:
            data_status = None

        if data['setup']['is_assign'] == 1:
            data_assign = (
                ts(),
                data['data']['action_id'],
                assign_id,
                data['data']['assign']['assign_to'])
            # Task().run_assign(data_assign)
        else:
            data_assign = None

        Task()._runtrans(data_action=data_action, data_task=task_transaction_data,
                         data_assign=data_assign, data_comment=data_comment, data_status=data_status)

    def _runtrans(self, data_action, data_task=None, data_assign=None, data_comment=None, data_status=None, data_sd=None):
        try:
            print('TSKMNGER.TRANS_ACTION: ', data_action)
            cur.execute((
                "INSERT INTO actions (dt, action_id, task_id, assign_id, comment_id, status_set_id, is_status_set, is_assign, is_comment, action_by_user) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"),
                data_action)
            if data_task is not None:
                print('TSKMNGER.TRANS_TASK: ', data_task)
                task_kid = Task().get_task_kid(data_task[4])
                data_taskid = [*data_task[0:2], task_kid, *data_task[2:13]]
                print(data_taskid)
                print('TSKMNGER.TRANS_TASK1: ', data_taskid)

                cur.execute((
                    "INSERT INTO task (dt, task_id, task_kid, task_usergroup, task_type, task_project, task_desc, task_tittle, user_on_task, status_on_task, glob_status, task_priority, task_dd, intask_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"),
                    data_taskid)

            if data_assign is not None:
                print('TSKMNGER.TRANS_ASSIGN: ', data_assign)
                cur.execute((
                    "INSERT INTO assign (dt, action_id, assign_id, assign_to) VALUES (?, ?, ?, ?)"),
                    data_assign)
                cur.execute("UPDATE task SET user_on_task = '{uon_task}' WHERE task_id = '{task_id}'".format(uon_task=data_assign[-1], task_id=data_action[2]))

            if data_comment is not None:
                print('TSKMNGER.TRANS_COMMENT: ', data_comment)
                cur.execute((
                    "INSERT INTO comment (dt, action_id, comment_id, author, caption, reply_action_id) VALUES (?, ?, ?, ?, ?, ?)"),
                    data_comment)
            if data_status is not None:
                cur.execute((
                    "INSERT INTO status (dt, action_id, status_set_id, status_set) VALUES (?, ?, ?, ?)"),
                    data_status)

                cur.execute("UPDATE task SET status_on_task = '{status_set}' WHERE task_id = '{task_id}'".format(
                    status_set=data_status[3], task_id=data_action[2]))

                if data_status[3] in Task().root_statuses[0]:
                    cur.execute(
                        "UPDATE task SET glob_status = 0 WHERE task_id = '{task_id}'".format(task_id=data_action[2]))

                print('TSKMNGER.TRANS_STATUS: ', data_status)
            db.commit()

        except:
            print('error')
            db.rollback()

    def get_task_db_id(self, task_id):
        data = cur.execute("SELECT id FROM task WHERE task_id == '{key}'".format(key=task_id)).fetchone()
        if not data:
            return None
        else:
            return data[0]

    def get_task_kid(self, task_project):
        kid = f'{task_project}-{taskdata().get_project_new_taskint(task_project)}'
        return kid

    def get_task_kid_by_id(self, task_id):
        data = cur.execute("SELECT task_kid FROM task WHERE task_id == '{key}'".format(key=task_id)).fetchone()
        if not data:
            return None
        else:
            return data[0]

    def is_task_exist(self, task_id):
        data = cur.execute("SELECT task_id FROM task WHERE task_id == '{key}'".format(key=task_id)).fetchone()
        if not data:
            print('NO_DATA ON TASK_ID, TRY KID')
            data = cur.execute("SELECT task_id FROM task WHERE task_kid == '{key}'".format(key=task_id)).fetchone()
            if data is not None:
                print('FOUND TASK_KID, RETURNED TASK_ID')
                return data[0]
            else:
                print('NO_DATA ON TASK_KID')
                return None

        else:
            return data[0]

    class utils:

        def get_task_full_info(self, task_id):
            task_id = Task().tid_check(task_id)
            act_status_id = taskdata().get_last_status_activity(task_id)
            act_status = taskdata().get_status_by_said(act_status_id)
            primary = taskdata().get_primary_info(task_id)
            comments_ids = taskdata().comments(task_id=task_id).get_ids()

            print(f'Tittle: {primary[5]}\n'
                  f'STATUS: {act_status}\n'
                  f'Issued: {primary[0]}\n'
                  f'TaskId: {primary[1]}\n'
                  f'TaskGroup: {primary[2]}\n'
                  f'Project: {primary[3]}\n'
                  f'Description: {primary[4]}'
                  f'COMMENTS:\n\n')
            for comment in comments_ids:
                # print("TSKMNGER. ", get_task_comment_data(comment[0]))
                print("TSKMNGER. ", taskdata().comments(comment_id=comment[0]).get_data())

        def load_comments(self, task_id):
            task_id = Task().tid_check(task_id)
            comments_ids = taskdata().comments(task_id=task_id).get_ids()
            for comment in comments_ids:
                # print("TSKMNGER. ", get_task_comment_data(comment[0]))
                print("TSKMNGER. ", taskdata().comments(comment_id=comment[0]).get_data())

def ts():
    a = dt.now().strftime("%Y-%m-%d %H:%M:%S")
    return a

