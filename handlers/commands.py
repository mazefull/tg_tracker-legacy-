from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from keyboard.builder import btni, btni_static
import json
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from tracker.manager import Task
from tracker.notificator import send_notify
from tracker.service import user_id_list, is_user_exist
from keyboard import static as skb

router = Router()

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

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    if await is_user_exist(message.chat.id) is False:
        await state.set_state(InitUser.fname)
        await message.answer('Ты ещё не зарегистрирован в системе.\nВведи свои Имя и Фимилию в формате Иван_Иванов')
    else:
        await message.answer(f'Привет! Ты уже зарегистрирован. Можешь пользоваться трекером')
        await message.answer(skb.start_text)
        await message.answer(skb.selectors_text['main'], reply_markup= await btni_static(data=skb.main_menu, adjust=1))


@router.message(Command(commands=['new_task']))
async def new_issue(message: Message, state: FSMContext):
    if await is_user_exist(message.chat.id) is False:
        await message.answer('Пропиши команду /start')
    else:
        await state.set_state(BuildTask.tittle)
        await message.answer('Ты в режиме создания задачи.\n'
                             'Тебе потребуется ввести название, описание, указать проект и исполнителя.\n'
                             'Для отмены процедуры введи команду /cancel')
        await message.answer('[TASK] Введите название задачи')


@router.message(Command(commands=['cancel']))
async def new_issue(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Процедура прервана. Возвращаемся в главное меню',
                            reply_markup=await btni_static(data=skb.main_menu,
                                                           adjust=1))


async def notify_new_task_assigned(chat_id, task_id):
    uid_selector = await user_id_list(chat_id)
    if uid_selector[0] == 'user':
        await send_notify(chat_id=uid_selector[1], text=f"NEW TASK FOR YOU: {task_id}")
    elif uid_selector[0] == 'usergroup':
        print(f'TRY SEND NOTIFY TO ALL GROUP? {uid_selector[1]}')
