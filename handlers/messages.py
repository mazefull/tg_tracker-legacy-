from aiogram import Router
from aiogram.types import Message, CallbackQuery
from keyboard.builder import btni, gensbtns, genmarkup, btni_static
import keyboard.static as skb
import json
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from handlers.commands import BuildTask, InitUser
from tracker.service import init_user, get_users_creds, get_groups, get_projects
from tracker.manager import Task
from tracker.notificator import send_notify
from aiogram_calendar import SimpleCalendar

router = Router()


@router.message(BuildTask.tittle)
async def new_task__upd_tittle(message: Message, state: FSMContext):
    await state.update_data(tittle=message.text)
    await state.set_state(BuildTask.desc)
    await message.answer('[TASK] Введите описание задачи')


@router.message(BuildTask.desc)
async def new_task__upd_desc(message: Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await state.set_state(BuildTask.project)
    projects = get_projects()
    if projects is None:
        await message.answer("[TASK] Нет проектов, отправь сообщение с названием нового проекта")
    else:
        mrk = gensbtns(projects)
        await message.answer("[TASK] Выбери проект или отправь название нового", reply_markup=mrk)


@router.message(BuildTask.project)
async def new_task__upd_project(message: Message, state: FSMContext):
    await state.update_data(project=message.text)
    await state.set_state(BuildTask.deadline)
    mrk = await SimpleCalendar().start_calendar()
    await message.answer('[TASK] Укажи дедлайн', reply_markup=mrk)


@router.callback_query(BuildTask.deadline)
async def new_task__upd_priority(callback: CallbackQuery, state: FSMContext):
    print(callback.data)
    rm = ((callback.data).split(':'))[2:5]
    if int(rm[1]) < 10:
        rm[1] = "0" + str(rm[1])
    deadline = f'{rm[0]}-{rm[1]}-{rm[2]}'
    await state.update_data(deadline=deadline)
    await state.set_state(BuildTask.priority)
    mrk = gensbtns(skb.priorities)
    await callback.message.answer('[TASK] Укажи приоритет', reply_markup=mrk)


@router.message(BuildTask.priority)
async def new_task__upd_priority(message: Message, state: FSMContext):
    await state.update_data(priority=message.text)
    await state.set_state(BuildTask.assign)
    mrk = gensbtns(skb.assign)
    await message.answer('[TASK] На кого назначить задачу', reply_markup=mrk)


@router.message(BuildTask.assign)
async def new_task__upd_assign(message: Message, state: FSMContext):
    selector = message.text
    if selector == "Пользователь":
        await state.update_data(special='user')
        await state.set_state(BuildTask.pre_send)
        print('Генерим юзеров по списку')
        mrk = genmarkup(await get_users_creds(), 1)
        await message.answer('Выбери пользователя', reply_markup=mrk)

    elif selector == 'Группа':
        await state.update_data(special='group')
        await state.set_state(BuildTask.pre_send)
        print('Генерим группы по списку')
        mrk = genmarkup(await get_groups())
        await message.answer('Выбери группу пользователей', reply_markup=mrk)

    elif selector == 'Без привязки':
        print('Назначаем на админа')
        await state.update_data(assign=None)
        await state.set_state(BuildTask.pre_send)


@router.callback_query(BuildTask.pre_send)
async def new_task__pre_send(callback: CallbackQuery, state: FSMContext):
    if (await state.get_data())['special'] != None:
        dt = tuple((callback.data).replace('(', '').replace("'", "").replace(")", "").split(","))
        await state.update_data(assign=dt[0])
        await state.update_data(assign_specify=dt[1])
    elif (await state.get_data())['special'] == 'group':
        await state.update_data(assign=callback.data)
        await state.update_data(assign_specify='usergroup')
    else:
        await state.update_data(assign=None)

    data = await state.get_data()
    print(data)

    mrk = gensbtns(('OK', 'Отменить'))
    await state.set_state(BuildTask.send)
    await callback.message.answer(f'Давай сверим данные:\n\n'
                                  f'Название: {data["tittle"]}\n'
                                  f'Описание: {data["desc"]}\n'
                                  f'Проект: {data["project"]}\n'
                                  f'Приоритет: {data["priority"]}\n'
                                  f'Дедлайн: {data["deadline"]}\n'
                                  f'Назначен: {data["assign_specify"]}\n\n'
                                  f'Подтверждаем?', reply_markup=mrk)


@router.message(BuildTask.send)
async def new_task__send(message: Message, state: FSMContext):
    if message.text == "OK":
        data = await state.get_data()
        if data['special'] == 'group':
            assign_to_tracker = [data['assign'], data['assign_specify']]
        else:
            assign_to_tracker = data['assign']

        task_id = Task().new_issue(tittle=data['tittle'], desc=data['desc'], project=data['project'],
                                   priority=data['priority'], assign=assign_to_tracker, user=message.chat.id,
                                   deadline=data["deadline"])
        await state.clear()
        await message.answer(f'Создана задача {task_id}', reply_markup=await btni_static(data=skb.main_menu, adjust=1))
        if data['special'] == 'user':
            await send_notify(chat_id=data['assign'],
                              text=f"Для тебя появилась новая задача: {task_id}",
                              reply_marlup=await btni('Посмотреть задачи', 'my_tasks'))
    else:
        await message.answer('Процедура прервана', reply_markup=await btni_static(data=skb.main_menu, adjust=1))


@router.message(InitUser.fname)
async def new_user__upd_fname(message: Message, state: FSMContext):
    fname = message.text
    if not "_" in fname:
        await message.answer('[REG] Неверный формат. Попробуй ещё раз')
    else:
        await state.clear()
        await init_user((message.chat.id, message.from_user.username, fname))
        await message.answer(f'[REG] Спасибо. Теперь можно пользоваться трекером')
        await message.answer(skb.start_text, reply_markup=await btni_static(data=skb.main_menu, adjust=1))
