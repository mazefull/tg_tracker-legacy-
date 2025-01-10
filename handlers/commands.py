import uuid

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from keyboard.builder import btni, btni_static
import json
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from tracker.manager import Task
from tracker.notificator import send_notify
from tracker.service import notifys, users, permit
from keyboard import static as skb

router = Router()

def fastsdvpn(message: Message):
    userid = message.chat.id
    if not message.from_user.username:
        uname = message.from_user.first_name
    else:
        uname = message.from_user.username
    intask_id = str(uuid.uuid4())[-12:]
    project = "VPNREQ"
    db_datasheet = 'vpn'
    task_id = Task().new_issue(tittle="VPNREQ",
                     intask_id=intask_id,
                     desc=f'Выдача доступа VPN для {userid} (@{uname})',
                     assign=276914408, project=project, task_type="SD", user=userid, deadline=0)
    Task().new_sd(intask_id, userid, userid, status_profile='REQUEST', sheet='vpn')
    Task().sd_task_worker(intask_id=intask_id, task_id=task_id, project=project, sheet=db_datasheet)



refcodes = {
    "privatedisco_vpn": fastsdvpn

}


class BuildTask(StatesGroup):
    tittle = State()
    desc = State()
    project = State()
    priority = State()
    deadline = State()
    assign = State()
    assign_specify = State()
    special = State()
    pre_send = State()
    send = State()


class SelectTask(StatesGroup):
    selector1 = State()
    selector2 = State()

class InitUser(StatesGroup):
    fname = State()
    select_permission = State()

class Console(StatesGroup):
    TaskMenu = State()
    TaskSelector = State()
    Action = State()
    ChangeStatus = State()
    ChangeStatusState = State()
    TaskAssign = State()
    TaskEdit = State()
    TaskNewComment = State()
    TaskNewCommentFixed = State()
    TaskMA = State()
    SD = State()
    SDNUM = State()
    SDPROJ = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # permit().main_menu_btns(userid=message.chat.id)
    # print(message.chat.id)
    # print('------------------')
    # permit().pc_role_unpacker(req_role="pc_default_team_adm")
    # print('------------------')


    refcode = None
    refcode = message.text[7:]
    print(refcode)
    try:
        refcodes[refcode](message)
    except KeyError:
        pass

    if users().is_user_exist(user_id=message.chat.id) is False:
        await state.set_state(InitUser.fname)
        await message.answer('Ты ещё не зарегистрирован в системе.\nВведи свои Имя и Фимилию в формате Иван_Иванов')
        if refcode is not None:
            await state.update_data(select_permission=refcode)

    else:
        if users().get_usergroup(userid=message.chat.id) is None:
            await message.answer(text='Тебе ещё не выдан доступ. Ожидай решения администратора, отправили ему нотификацию')
            data = users().get_task_registation_request(message.chat.id)
            await send_notify(chat_id=data[2],
                              text=f'Пользователь {message.chat.id} (@{message.from_user.username}) повторно запросил выдачу пермишена.\n\n'
                                   f'Операционный таск: {data[1]}',
                              reply_marlup= await btni('Открыть задачи', 'my_tasks'))

        else:
            await message.answer(f'Привет! Ты уже зарегистрирован. Можешь пользоваться трекером')
            await message.answer(skb.start_text)
            # button_from_permission = skb.main_menu_tasks_permisson_chart[permit().main_menu_btns(userid=message.chat.id)]

            # await message.answer(skb.selectors_text['main'],
            #                      reply_markup=await btni_static(data=button_from_permission, adjust=1))

            await message.answer(skb.selectors_text['main'], reply_markup= await btni_static(data=skb.main_menu, adjust=1))


@router.message(Command(commands=['new_task']))
async def new_issue(message: Message, state: FSMContext):
    if users().is_user_exist(user_id=message.chat.id) is False:
        await message.answer('Пропиши команду /start')
    else:
        await state.set_state(BuildTask.tittle)
        await message.answer('Ты в режиме создания задачи.\n'
                             'Тебе потребуется ввести название, описание, указать проект и исполнителя.\n'
                             'Для отмены процедуры введи команду /cancel')
        await message.answer('[TASK] Введите название задачи')


@router.message(Command(commands=['ntfc']))
async def manual_notify(message: Message, state: FSMContext):
    if users().get_usergroup(message.chat.id) == 'admin':

        await send_notify(chat_id=5167881010, text='Хуй тебе, <a href="https://img01.kupiprodai.ru/062024/1717678288513.jpg">вот такой</a>\n\n ')






@router.message(Command(commands=['cancel']))
async def new_issue(message: Message, state: FSMContext):

    await state.clear()
    await message.answer('Процедура прервана. Возвращаемся в главное меню',
                            reply_markup=await btni_static(data=skb.main_menu,
                                                           adjust=1))


async def notify_task_assigned(task_id):
    users2notify = notifys().get_users_to_notify(task_id=task_id)
    print(users2notify)
    for user in users2notify:
        await send_notify(chat_id=user, text=f"NEW TASK FOR YOU: {task_id}")
