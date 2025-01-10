import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from handlers.messages import notify_user
from keyboard.builder import btni, btni_static, genmarkup
from keyboard import static as skb
import json
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from handlers.commands import BuildTask, Console
from tracker.service import usp, users, taskdata, create_sd_sheet, create_vpn_sheet
from tracker.manager import Task
from handlers.commands import SelectTask

router = Router()
asyncio.run(create_sd_sheet())

def get_procedures():
    templates_name = list(skb.informer_tasks["templates"].keys())
    templates = []
    for name in templates_name:
        templates.append((skb.informer_tasks["templates"][name]["procedure"], name))
    return templates

def build_buttons_from_dict(data):
    buttons_names = list(data.keys())
    result = []
    for names in buttons_names:
        result.append((data[names]["action"], data[names]["text"]))
    return result


class Informer(StatesGroup):
    tag_last_menu = State()
    tag_next_menu = State()
    main_menu = State()

class INFRA_VPN(StatesGroup):
    vpn_use_mode = State()
    vpn_select_target_pre = State()
    vpn_select_target = State()
    vpn_prepare_data = State()
    vpn_send_request = State()

class AutoBlock(StatesGroup):
    procedure_data = State()
    stage_selector = State()
    main_resolver = State()
    sub_stage_id = State()
    sub_stage_data = State()
    sub_stage_selector = State()
    stage1 = State()
    stage2 = State()
    stage3 = State()
    stage4 = State()
    stage5 = State()
    param1 = State()
    param2 = State()
    param3 = State()
    param4 = State()
    param5 = State()



async def gen_users_list_for_markup():
    mrk = genmarkup(await users().get_users_creds(), 1)
    return mrk

async def gen_groups_list_for_markup():
    mrk = genmarkup(await users().get_groups())
    return mrk


json_requests = {
    "users_list_all": gen_users_list_for_markup(),
    "groups_list_all": gen_groups_list_for_markup()

}




@router.callback_query(F.data == 'informer_main')
async def informer_main(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(text=skb.selectors_text['informer_main'],
                                     reply_markup=genmarkup(get_procedures()), callback_data='main_menu')

# @router.callback_query(F.data == "infreq_vpn")
# async def infreq_vpn_master(callback: CallbackQuery, state: FSMContext):
#     procedure_data = skb.informer_tasks["procedures"]["infreq"]["infreq_vpn"]
#     await create_vpn_sheet()
#     await state.set_state(INFRA_VPN.vpn_use_mode)
#     user_group = users().get_usergroup(callback.message.chat.id)
#     try:
#         way_group = procedure_data["bp_ways"]["way_groups"][user_group]
#     except:
#         way_group = procedure_data["bp_ways"]["way_groups"]["default"]
#     await state.update_data(vpn_use_mode=way_group)
#     ws = INFRA_VPN.vpn_select_target
#     await state.set_state(ws)
#
#     bp_way_data = procedure_data["bp_ways"][way_group]
#
#     await callback.message.edit_text(text=bp_way_data["main"]["text"],
#                                      reply_markup=genmarkup(build_buttons_from_dict_list(bp_way_data["main"]["buttons"])), callback_data='main_menu')


@router.callback_query(F.data == "infreq_vpn")
async def infreq_vpn_master(callback: CallbackQuery, state: FSMContext):
    await state.set_state(INFRA_VPN.vpn_use_mode)
    default_flag = True
    if default_flag:
        user_group = "default"
    else:
        user_group = users().get_usergroup(callback.message.chat.id)
    print(f'state.vpn_use_mode: {user_group}')
    await state.update_data(vpn_use_mode=user_group)
    mrk = await btni_static(skb.infreq_vpn_master[user_group], adjust=1)
    await callback.message.edit_text(text='Выбери тематику запроса', reply_markup=mrk)


# @router.message(INFRA_VPN.vpn_use_mode)
# async def infreq_vpn_use_mode(message: Message, state: FSMContext):
#     use_mode = (await state.get_data())["vpn_use_mode"]
#     thematic = callback.data
#     if use_mode == "default":
#         if thematic == "infreq_vpn_request":
#             await callback.message.edit_text(text="Опиши, зачем тебе нужен доступ к VPN")


@router.message(AutoBlock.main_resolver)
async def auto_main(message: Message, callback: CallbackQuery, state: FSMContext):
    """
    state.stage_selector — В stage_selector вносим данные стэйта,
    На который должно быть переключение, но в рамках автоблока всё обрабатывает один мэйн стейт.

    state.procedure_data — Параметры процедуры.

    stage_now — Узнаём текущий этап процедуры из stage_selector.

    stage_now_data — Dытаскиваем из стейта данные по ключу stage_now. main_resolver будет недостаточно собственной глубины,
    будет использоваться последовательное хранение по sub_stage_id.

    sub_stage_id — создаётся на основе uid4:12 c порядковым номером по пути процедуры. Хранится массивом.

    :param message:
    :param callback:
    :param state:
    :return:
    """

    state_data = await state.get_data()     #Запрос всей памяти стейта
    procedure_data = state_data["procedure_data"]       #Параметры процедуры
    state_now = await state.get_state()     #Узнаём текущий стейт
    stage_now = state_data["stage_selector"]        #Узнаём текущий стэйдж процедуры. В stage_selector вносим данные стэйта,
                                                    #На который должно быть переключение, но в рамках автоблока всё обрабатывает один мэйн стейт
    stage_now_data = state_data[stage_now]      #Запрос памяти текущего стэйджа
    message_data = message
    callback_data = callback
    print(f"[stage_now]: {stage_now}\n"
          f"[state_now]: {state_now}\n"
          f"[message][{message_data.chat.id}:] {message_data.text}\n"
          f"[callback][{callback_data.message.chat.id}:] {callback_data.message.text}")
