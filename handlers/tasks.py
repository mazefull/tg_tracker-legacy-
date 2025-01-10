from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import modules.mods.vpn_vps_worker.vpn_worker
from handlers.messages import notify_user
from keyboard.builder import btni, btni_static, genmarkup
from keyboard import static as skb
import json
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from handlers.commands import BuildTask, Console
from tracker.notificator import send_notify
from tracker.service import usp, users, taskdata, permit
from tracker.manager import Task
from handlers.commands import SelectTask

router = Router()


@router.callback_query(F.data == 'main_menu')
async def main_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(text=skb.selectors_text['main'],
                                  reply_markup=await btni_static(data=skb.main_menu,
                                                                 adjust=1))

@router.callback_query(F.data == 'main_menu_tasks')
async def main_menu_tasks(callback: CallbackQuery, state: FSMContext):
    button_from_permission = skb.main_menu_tasks_permisson_chart[permit().main_menu_btns(userid=callback.message.chat.id)]

    await callback.answer()
    await state.clear()
    await callback.message.edit_text(text=skb.selectors_text['main'],
                                     reply_markup=await btni_static(data=button_from_permission,
                                                                    adjust=1))




@router.callback_query(F.data == 'new_task')
async def menu_new_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(BuildTask.tittle)
    await callback.message.edit_text(text=f'{skb.new_task_intro}\n\n[TASK] Введите название задачи')

@router.callback_query(F.data == 'faq')
async def faq(callback: CallbackQuery):
    await callback.message.edit_text(text=skb.faq_into,
                                     reply_markup= await btni_static(skb.faq_btns,
                                                                     adjust=1))

@router.callback_query(F.data == 'faq_how_issue')
async def faq_how_issue(callback: CallbackQuery):
    await callback.message.edit_text(text=skb.how_issue,
                                     reply_markup=await btni(('Назад', 'Главное меню'),
                                                             ('faq', 'main_menu'),
                                                             adjust=1))

@router.callback_query(F.data == 'faq_how_edit')
async def faq_how_edit(callback: CallbackQuery):
    await callback.message.edit_text(text=skb.how_edit,
                                     reply_markup=await btni(('Назад', 'Главное меню'),
                                                             ('faq', 'main_menu'),
                                                             adjust=1))

@router.callback_query(F.data == 'faq_notify')
async def faq_faq_notify(callback: CallbackQuery):
    await callback.message.edit_text(text=skb.faq_notify,
                                     reply_markup=await btni(('Назад', 'Главное меню'),
                                                             ('faq', 'main_menu'),
                                                             adjust=1))

@router.callback_query(F.data == 'my_tasks')
async def menu_my_tasks(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SelectTask.selector1)
    data = await taskdata().get_active_tasks(callback.message.chat.id)
    button_from_permission = skb.main_menu_tasks_permisson_chart[permit().main_menu_btns(userid=callback.message.chat.id)]

    if data is None:
        try:
            await callback.message.edit_text(text='У тебя нет активных задач',
                                             reply_markup=await btni_static(data=button_from_permission,
                                                                            adjust=1))
        except:
            await callback.message.answer(text='У тебя нет активных задач',
                                             reply_markup=await btni_static(data=button_from_permission,
                                                                            adjust=1))
    else:
        await state.set_state(Console.TaskSelector)
        mrk = genmarkup(data)
        try:
            await callback.message.edit_text(text='Список твоих активных задач',
                                             reply_markup=mrk)
        except:
            await callback.message.answer(text='Список твоих активных задач',
                                             reply_markup=mrk)

@router.callback_query(F.data == 'all_tasks')
async def menu_all_tasks(callback: CallbackQuery, state: FSMContext):
    button_from_permission = skb.main_menu_tasks_permisson_chart[permit().main_menu_btns(userid=callback.message.chat.id)]
    await callback.answer()
    await state.set_state(SelectTask.selector1)
    await state.update_data(selector1=True)
    data = await taskdata().get_all_active_tasks()
    if data is None:
        try:
            await callback.message.edit_text(text='На данный момент нет нет активных задач',
                                             reply_markup=await btni_static(data=button_from_permission,
                                                                            adjust=1))
        except:
            await callback.message.answer(text='На данный момент нет нет активных задач',
                                             reply_markup=await btni_static(data=button_from_permission,
                                                                            adjust=1))

    else:
        await state.set_state(Console.TaskSelector)
        mrk = genmarkup(data)
        try:
            await callback.message.edit_text(text='Список активных задач',
                                             reply_markup=mrk)
        except:
            await callback.message.answer(text='Список активных задач',
                                             reply_markup=mrk)


@router.callback_query(Console.TaskSelector)
async def selected_task(callback: CallbackQuery, state: FSMContext):
    selector = callback.data
    default_markup = await btni_static(skb.task_menu_main,
                                       adjust=1)


    await state.update_data(TaskSelector=selector)
    print(selector)
    task_data = await taskdata().prepare_get_post(selector)
    main_poster = task_data[0]
    temp = False

    if task_data[1] is not None:
        temp = True
        intask_id = task_data[1]
        print("Найден связанный SD-запрос")
        if users().get_usergroup(callback.message.chat.id) == 'admin':
            main_poster = main_poster + "\n\n<b>Найден связанный SD-запрос</b>"

            await state.set_state(Console.SDNUM)
            await state.update_data(SDNUM=intask_id)


            default_markup = await btni_static(skb.task_menu_main_sd, adjust=1)

    await state.set_state(SelectTask.selector1)
    try:
        if (await state.get_data())["selector1"]:
            if temp:
                mrk = await btni_static(skb.all_task_menu_main_sd,
                                        adjust=1)
            else:
                mrk = await btni_static(skb.all_task_menu_main,
                                    adjust=1)
        else:
            mrk = default_markup
    except:
        mrk = default_markup


    await state.set_state(Console.TaskMenu)
    await callback.message.edit_text(text=main_poster,
                                     reply_markup=mrk,
                                     parse_mode='HTML')

@router.callback_query(Console.TaskMenu)
async def selected_task_menu(callback: CallbackQuery, state: FSMContext):
    button_from_permission = skb.main_menu_tasks_permisson_chart[permit().main_menu_btns(userid=callback.message.chat.id)]
    print(f'Console.TaskMenu: {callback.data}')
    if callback.data == "task_make_action":
        await state.set_state(Console.Action)
        # await callback.message.edit_reply_markup(reply_markup=await btni_static(data=button_from_permission,
        #                     adjust=1))
        await callback.message.edit_reply_markup(reply_markup=await btni_static(data=skb.task_menu_actions,
                                                                                adjust=1))
    elif callback.data == "task_load_comments":
        print('LOAD COMMENTS')
        task_id = (await state.get_data())['TaskSelector']
        # Task().utils().load_comments(task_id=task_id)
        await state.set_state(Console.TaskSelector)
        dataset = taskdata().comments().prepare_comments_poster(task_id)
        await callback.message.edit_text(text=dataset,
                                         reply_markup=await btni(text='Назад к задаче', callback_data=(await state.get_data())["TaskSelector"]))
    elif callback.data == 'my_tasks':
        await callback.answer()
        await state.set_state(SelectTask.selector1)
        data = await taskdata().get_active_tasks(callback.message.chat.id)
        if data is None:
            try:
                await callback.message.edit_text(text='У тебя нет активных задач',
                                                 reply_markup=await btni_static(data=button_from_permission,
                                                                                adjust=1))
            except:
                await callback.message.answer(text='У тебя нет активных задач',
                                              reply_markup=await btni_static(data=button_from_permission,
                                                                             adjust=1))
        else:
            await state.set_state(Console.TaskSelector)
            mrk = genmarkup(data)
            try:
                await callback.message.edit_text(text='Список твоих активных задач',
                                                 reply_markup=mrk)
            except:
                await callback.message.answer(text='Список твоих активных задач',
                                              reply_markup=mrk)
    elif callback.data == 'SD_MA':
        console_state_data = (await state.get_data())
        sdnum = console_state_data['SDNUM']
        print(f'Переходим в меню управления SD-запросом. \nTask: {console_state_data["TaskSelector"]}\nSD: {sdnum} ')
        sd_project = taskdata().get_sd_project(intask_id=sdnum)
        await state.update_data(SDPROJ=sd_project)
        markup = await btni_static(skb.sd_buttons[sd_project], adjust=(2, 1))
        await callback.message.edit_text(text="Что нужно сделать с запросом?", reply_markup=markup)
        await state.set_state(Console.SD)

@router.callback_query(Console.SD)
async def sd_worker(callback: CallbackQuery, state: FSMContext):
    button_from_permission = skb.main_menu_tasks_permisson_chart[permit().main_menu_btns(userid=callback.message.chat.id)]
    print(f'Console.SD.ACTION: {callback.data}')
    console_state_data = (await state.get_data())
    sdnum = console_state_data["SDNUM"]
    task = console_state_data["TaskSelector"]
    project = console_state_data["SDPROJ"]
    target = taskdata().get_sd_target(sdnum)
    if callback.data == "sd_ok":
        await callback.answer('Передаём задание в SD-WORKER')
        ramp = "test"
        from uuid import uuid4
        uid = str(uuid4())[:5]
        profile_name = str(ramp) + "_" + uid
        ds = (profile_name, target)
        print(ds)
        sd_result = None
        if sd_result is not None:
            sd_result = modules.mods.vpn_vps_worker.vpn_worker.vps_new_profile(*ds)
            print('Пропускаем выдачу профиля')

        if sd_result is not False:
            task_kid = Task().get_task_kid_by_id(task)
            Task().sd_status_action(intask_id=sdnum, status="APPROVE")
            Task().multi_action(task_id=task, assign_to=target, user_id=callback.message.chat.id, comment='Доступ успешно выдан', status_to='Выполнено')
            await notify_user(chat_id=target, special='Выполнено действие по твоему запросу: ', task_id=task_kid)

    if callback.data.startswith("accs_"):
        usergroup = (str(callback.data).split("_"))[1]
        # target = users().get_target_by_intask_id(intask_id=sdnum)
        chuck = permit().set_user_usergroup(userid=target, usergroup=usergroup)
        if chuck:
            await callback.answer('Доступ выдан успешно')
            await send_notify(chat_id=target, text=f'Вам был выдан доступ. USERGROUP: {usergroup}')
            Task().multi_action(task_id=task, status_to='DONE')
            Task().sd_status_action(intask_id=sdnum, status="DONE")
            print('EXCEPTION')
            await callback.message.edit_text(text='Возвращаемся в меню управления задачами', reply_markup = await btni_static(data=button_from_permission,
                                             adjust=1))


        else:
            print('error')


@router.callback_query(Console.Action)
async def selected_task_actions(callback: CallbackQuery, state: FSMContext):
    print('TT. Console.Action', callback.data)
    if callback.data == 'task_change_status':
        await state.set_state(Console.ChangeStatus)
        mrk = await btni_static(skb.task_status_list,
                                adjust=1)

        await callback.message.edit_text('Выбери новый статус',
                                         reply_markup=mrk)

    elif callback.data == 'task_assign':
        await state.set_state(Console.TaskAssign)
        await callback.message.edit_text('На кого назначить задачу?',
                                         reply_markup=genmarkup(await users().get_users_creds(),
                                                                1))

    elif callback.data == 'task_edit':
        await callback.message.edit_text('Редактирование описания, заголовка и дедлайнов пока недоступно',
                                         reply_markup=await btni_static(skb.task_menu_actions,
                                                                        adjust=1))
        # await state.set_state(Console.TaskAssign)
        # await callback.message.edit_text('Что ты хочешь изменить?',
        #                                  reply_markup=await btni_static(skb.task_editions_list,
        #                                                                 adjust=1))

    elif callback.data == 'task_new_comment':
        await state.set_state(Console.TaskNewComment)
        await callback.message.edit_text('Напиши комментарий')

    elif callback.data == 'task_only_comment':
        data = await state.get_data()
        comment = data['TaskNewComment']
        await state.set_state(Console.TaskNewCommentFixed)
        mrk = await btni(('Всё верно', 'Переписать', 'Отменить'), ('send', 'repeat', 'reject'), 1)
        await callback.message.answer(f'Давай сверимся. Добавляем к задаче следующий комментарий:\n\n{comment}', reply_markup=mrk)


@router.callback_query(Console.ChangeStatus)
async def task_change_status(callback: CallbackQuery, state: FSMContext):
    selector = (await state.get_data())['TaskSelector']
    print(selector)
    print(callback.data)
    if callback.data not in skb.task_status_list[1]:
        mrk = await btni_static(skb.task_status_list,
                                adjust=1)

        await callback.message.edit_text('Неверный статус, попробуй ещё раз',
                                         reply_markup=mrk)

    else:
        await state.update_data(ChangeStatus=callback.data)
        await state.set_state(Console.ChangeStatusState)
        if skb.task_status_next_actions["let_assign"][callback.data]:
            mrk = await btni(('Yes', 'No'),
                             ('status_need_assign', 'status_done'),
                             1)
            await callback.message.edit_text('Отлично! Скажи, нужно переназначить задачу на другого пользователя?',
                                             reply_markup=mrk)
        else:
            mrk = await btni(('Подтвердить', 'Отмена'), (callback.data, 'main_menu_tasks'))
            await callback.message.edit_text(f'Подтверждаем смену статуса на: {callback.data}?',
                                             reply_markup=mrk)

@router.callback_query(Console.ChangeStatusState)
async def task_change_status(callback: CallbackQuery, state: FSMContext):
    print(callback.data)
    if callback.data in ('status_done', 'status_trashed'):
        data = await state.get_data()
        print('PRE SEND TO DB/ NO_ASSIGN: ', data)
        try:
            comment = data['TaskNewComment']
        except:
            comment = None


        Task().multi_action(task_id=data['TaskSelector'],
                            status_to=skb.status_mware[data['ChangeStatus']],
                            user_id=callback.message.chat.id,
                            comment=comment)

        mrk = await btni_static(data=skb.main_menu,
                                adjust=1)
        await callback.message.edit_text(text='Всё готово. Возвращаемся в главное меню',
                                         reply_markup=mrk)


    elif callback.data == 'status_need_assign':
        await state.update_data(ChangeStatusState=1)
        await state.set_state(Console.TaskAssign)
        mrk = genmarkup(await users().get_users_creds(), 1)
        await callback.message.edit_text('Укажи, на кого хочешь назначить задачу',
                                         reply_markup=mrk)

@router.callback_query(Console.TaskAssign)
async def task_change_assignation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selector = data['TaskSelector']
    assign = usp(callback.data)
    user_id = callback.message.chat.id

    try:
        status_to = data['ChangeStatus']

    except:
        status_to = None

    try:
        comment = data['TaskNewComment']
    except:
        comment = None

    print(assign)
    if users().is_user_exist(assign[0]):
        Task().multi_action(task_id=selector,
                            status_to=status_to,
                            assign_to=assign[0],
                            user_id=user_id,
                            comment=comment)

        await notify_user(chat_id=assign[0],
                          task_id=Task().get_task_kid_by_id(data['TaskSelector']),
                          special="ASSIGN")

        await state.clear()
        await callback.message.edit_text(text='Всё готово. Возвращаемся в главное меню',
                                         reply_markup=await btni_static(data=skb.main_menu,
                                                                        adjust=1))
    else:
        await state.clear()
        await callback.message.edit_text(text='ВНИМАНИЕ: ИНЦИДЕНТ ERRS-1\nВозникла ошибка при назначении задачи, возвращаемся в главное меню',
                                         reply_markup=await btni_static(data=skb.main_menu,
                                                                        adjust=1))


@router.message((Console.TaskNewComment))
async def task_new_comment_handler(message: Message, state: FSMContext):
    comment = message.text
    await state.update_data(TaskNewComment=comment)
    await state.set_state(Console.Action)
    mrk = await btni(('Статус', 'Исполнитель', 'Нет'), ('task_change_status', 'task_assign', 'task_only_comment'))
    await message.answer('Отлично, записал новый комментарий!\n\nСкажи, нужно сменить статус задачи или исполнителя?',
                         reply_markup=mrk)

@router.callback_query(Console.TaskNewCommentFixed)
async def task_new_comment_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == 'send':
        Task().multi_action(task_id=data['TaskSelector'],
                            comment=data['TaskNewComment'],
                            user_id=callback.message.chat.id)

        await callback.message.edit_text(text='Всё готово. Возвращаемся в главное меню',
                                         reply_markup=await btni_static(data=skb.main_menu,
                                                                        adjust=1))
    if callback.data == 'repeat':
        await state.set_state(Console.TaskNewComment)
        await callback.message.edit_text('Напиши комментарий')

    if callback.data == 'reject':
        await state.clear()
        await callback.message.edit_text('Процедура прервана. Возвращаемся в главное меню',
                                         reply_markup=await btni_static(data=skb.main_menu,
                                                                        adjust=1))