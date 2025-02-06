projects = ('BOT', 'QA', 'CAFEE', 'MARKET')

priorities = ('Обычный', 'Срочный', 'ASAP')

tasks_search_type = ('По ID', 'По проекту', 'По исполнителю')

assign = ('Пользователь', 'Группа')


start_text_null = ("ВНИМАНИЕ!! Это не финальная версия ПО. Полноценно готов только движок трекера. "
              "Через бота на данный момент можно создавать задачи и назначать на исполнителя при создании. "
              "Исполнителю приходит уведомление о появлении новой задачи.\n\n"
              "Совсем скоро можно будет сразу открыть описание задачи при поступлении уведомления, "
              "будут интегрированы комментарии, смена статусов, создание проектов, просмотр задач отдельно по каждоиу проекту")

start_text = ('ВНИМАНИЕ!! Это не финальная версия ПО. Часть функций пока что в разработке. '
              'Инструкции по использованию можно посмотреть в разделе FAQ\n\nВыход в главное меню осуществляется по команде /cancel')


faq_into = ('Реализованный функционал:\n'
                                     '1. Создание задач;\n'
                                     '2. Назначение задач, изменение статусов, добавление комментариев;\n'
                                     '3. Отправка уведомлений о назначении задачи;\n'
                                     '4. Уведомление о приближении дедлайна;\n\n'
            '5. Отображение комментариев под задачей;\n'
                                     'В разработке:\n'
                                     '1. Админ панель и личный профиль;\n'
                                     '2. Создание общих задач;\n'
                                     '3. Редактирование описания задачи и изменение дедлайнов\n'
            
            '4. Отображение истории действий по задаче;\n'
            '5. Исправление отрицательного остатка дней при нотификации по дедлайнам\n'
            '6. Специальные нотификации;')

how_issue = ('Для создания задач нужно перейти в главное меню. Через /start → Работа с задачами, либо по команде /new_task. '
             'Будут запрошены различные вводные, после чего нужно будет сверить данные и подтвердить задачу')

how_edit = ('Сейчас доступны для редактирования только задачи, назначенные на тебя лично. '
            'Можно менять статус, переназначать на другого пользователя, добавлять комментарии')

faq_notify = ('Сейчас отправляются уведомления при назначении как новой задачи на пользователя, так и при переназначении задачи. '
              'Также, приходит уведомление при приближении к дедлайну')


faq_btns = (('Создание задачи', 'Изменение задач', 'Нотификации', 'Назад'),
            ('faq_how_issue', 'faq_how_edit', 'faq_notify', 'main_menu'))


selectors_text = {
    "main": "Выбери пункт меню",
    "task": "Что ты хочешь сделать с задачей?",
    "search": "Как будем искать?",
    "action": "Выбери действие",
    "informer_main": "Ты находишься в меню быстрых задач, выбери тематику и отправь на исполнение",
    "informer_trash": "Шо вылупился пидарняга😘"
}

informer_tasks = {
    "templates": {
        "VPN": {
            "tittle": "Запрос доступа к OVPN",
            "procedure": "infreq_vpn",
            "ownergroup": "admin",
        },
        "MEET": {
            "tittle": "Организация встречи",
            "procedure": "infreq_offer_meet",
            "ownergroup": "admin",
        }
    },
    "procedures": {
        "infreq": {
            "infreq_vpn": {
                "main": {
                    "tittle_description": "Выдача доступа к VPN",
                    "data": {
                        "setup": {
                            "db": "default",
                            "table": "vpn",  #таблица пользователей VPN
                            "table_template": "vpn_users",  #Шаблон таблицы пользователей
                            "task_data_template": "vpn_tasks_data",  #Шаблон данных для связи запроса
                            "task_link_type": "intask_id"  #Тип связи данных с таском
                        },
                        "templates": {
                            "vpn_users": {
                                "dt": "dt",
                                "intask_id": "intask_id",
                                "target": "target",
                                "issuer": "issuer",
                                "requestor": "requestor",
                                "status": "status"
                            },
                            "vpn_tasks_data": {
                                "uname": "uname",
                                "target": "target",
                                "issuer": "issuer",
                                "requestor": "requestor"
                            }
                        }
                    },
                    "buttons": {
                        0: {
                            "text": "Выдать доступ",
                            "action": "gather_vpn_easy"
                        },
                        1: {
                            "text": "Создать задачу",
                            "action": "task_vpn_easy"
                        }
                    }
                },
                "bp_ways": {
                    "way_groups": {
                        "admin": "infreq_vpn_easy",
                        "operator": "easy1",
                        "default": "hard"

                    },
                    "infreq_vpn_easy": {
                        "task": "ADMIN_VPN_GATHER",
                        "task_type": "async_auto",
                        "main": {
                            "text": "Выбери кому хочешь выдать доступ",
                            "buttons": {
                                "isdef": False,
                                "list": {
                                    "Пользователь": "easy_vpn_chs_user",
                                    "Группа": "easy_vpn_set_group"
                                },
                                "main_button": {
                                    "Выход": "informer_main"
                                }
                            }
                        },
                        "easy_vpn_chs_user": {
                            "text": "Выбери пользователя для выдачи доступа",
                            "buttons": {
                                "isdef": True,
                                "list": {
                                "def": "users_list_all",
                                "def_nextway": "easy_vpn_set_user"
                                },
                                "main_button": {
                                    "Выход": "infreq_vpn_easy"
                                }
                            }
                        },
                        "easy_vpn_set_user": {
                            "text": "Подтверди выдачу доступа для ",
                            "buttons": {
                                "isdef": False,
                                "list": {
                                    "Подтвердить": "bp_vpn_send_vps"
                                },
                                "main_button": {
                                    "Отменить": "infreq_vpn_easy"
                                },
                            }


                        },

                    },
                    "bp_vpn_send_vps": {
                        "use_call": True,
                        "call_def": "master_send_vps_gather_vpn",
                        "end_func": "informer_main"
                    },
                },
                "calls": {
                    "master_send_vps_gather_vpn": {
                            "is_call": True,
                            "call_def": "send_vps_action_vpn",
                            "call_data": {
                                "uname": "uname",
                                "target": "target",
                                "issuer": "issuer",
                                "requestor": "requestor"
                            }


                    }

                }


            }

        }

    }
}


infreq_vpn_master = {
    "default": (("Запрос доступа", "Проблемы в работе"),
                ("infreq_vpn_request", "infreq_vpn_issue")),
    "admin": (("Выдать доступ", "Service Desk"),
              ("infreq_vpn_adm", "infreq_vpn_sd_main"))
}




new_task_intro = ('Ты в режиме создания задачи.\n'
                  'Тебе потребуется ввести название, описание, указать проект и исполнителя.\n'
                  'Для отмены процедуры введи команду /cancel')


# main_menu = (('Работа с задачами', 'Мой профиль', 'FAQ'), ('main_menu_tasks', '🛑account', 'faq'))
main_menu = (('Работа с задачами', 'FAQ'), ('main_menu_tasks', 'faq'))


# main_menu_tasks = (('Создать задачу', 'Мои задачи', 'Поиск задач', 'Главное меню'),
#                    ('new_task', 'my_tasks', 'tasks_search', 'main_menu'))

main_menu_tasks = (('Создать задачу', 'Мои задачи', 'Все задачи', 'INFORMER', 'Главное меню'),
                   ('new_task', 'my_tasks', 'all_tasks', 'informer_main', 'main_menu'))

main_menu_tasks_no_search = (('Создать задачу', 'Мои задачи', 'INFORMER', 'Главное меню'),
                   ('new_task', 'my_tasks', 'informer_main', 'main_menu'))

main_menu_tasks_no_informer = (('Создать задачу', 'Мои задачи', 'Все задачи', 'Главное меню'),
                   ('new_task', 'my_tasks', 'all_tasks', 'main_menu'))

main_menu_tasks_no_na = (('Создать задачу', 'Мои задачи', 'Главное меню'),
                   ('new_task', 'my_tasks', 'main_menu'))

main_menu_tasks_permisson_chart = {
    "main_menu_tasks" : (('Создать задачу', 'Мои задачи', 'Все задачи', 'INFORMER', 'Главное меню'),
                   ('new_task', 'my_tasks', 'all_tasks', 'informer_main', 'main_menu')),
    "main_menu_tasks_no_search": (('Создать задачу', 'Мои задачи', 'INFORMER', 'Главное меню'),
                   ('new_task', 'my_tasks', 'informer_main', 'main_menu')),
    "main_menu_tasks_no_informer": (('Создать задачу', 'Мои задачи', 'Все задачи', 'Главное меню'),
                   ('new_task', 'my_tasks', 'all_tasks', 'main_menu')),
    "main_menu_tasks_no_na": (('Создать задачу', 'Мои задачи', 'Главное меню'),
                   ('new_task', 'my_tasks', 'main_menu'))
}

task_menu_main_permisson_chart = {




}




new_task = (('По шаблону', 'Ручной запрос'),
            ('new_task_example', 'new_task_manual'))



task_menu_main = (('Действие', 'Комментарии', 'К моим задачам'),
                  ('task_make_action', 'task_load_comments', 'my_tasks'))

all_task_menu_main = (('Действие', 'Комментарии', 'Ко всем задачам'),
                  ('task_make_action', 'task_load_comments', 'all_tasks'))


task_menu_main_sd = (('Действие', 'Комментарии', 'SD', 'К моим задачам'),
                  ('task_make_action', 'task_load_comments', 'SD_MA', 'my_tasks'))

all_task_menu_main_sd = (('Действие', 'Комментарии', 'SD', 'Ко всем задачам'),
                  ('task_make_action', 'task_load_comments', 'SD_MA', 'all_tasks'))


sd_buttons = {
    "VPNREQ": (("APPROVE", "DISCARD", "QUIT"), ("sd_ok", "sd_discard", "sd_exit")),
    "RREQ": (("GRANT DEFAULT", "GRANT ADMIN", "QUIT"), ("accs_default", "accs_admin", "sd_exit"))

}



task_menu_actions = (('Статус', 'Назначить', 'DONT TOUCH', 'Комментарий'),
                     ('task_change_status', 'task_assign', 'task_new_comment', 'task_new_comment'))


task_status_list = (('Готово', 'Отложить', 'Уточнить', 'Отменить'),
                    ('status_done', 'status_delayed', 'status_question', 'status_trashed'))

status_mware = {
    'status_done': "DONE",
    'status_in_work': "INWORK",
    'status_delayed': 'DELAYED',
    'status_question': 'WAIT FOR INFO',
    'status_trashed': 'TRASHED'
}


task_status_next_actions = {
    "let_assign": {
        "status_done": False,
        "status_in_work": False,
        "status_delayed": True,
        "status_question": True,
        "status_trashed": False
        }
    }

task_editions_list = (("Заголовок", 'Описание', 'Дедлайн'),
                      ('task_edit_tittle', 'task_edit_desc', 'task_edit_deadline'))


admin_order_menu_actions = (('🛑Статус', '🛑Назначить', '🛑Редактировать', 'Вложения', 'Оплата', 'Контакт', 'Админ меню'),
                           ('task_change_status', 'task_assign', 'task_edit', 'files', 'task_payment', 'task_get_user', 'issues_mgmt_mode'))