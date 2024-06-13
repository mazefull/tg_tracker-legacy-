from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboard.builder import btni, btni_static, genmarkup
from keyboard import static as skb
import json
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from handlers.commands import BuildTask
from tracker.service import get_active_tasks
from handlers.commands import SelectTask

router = Router()


@router.callback_query(F.data == 'main_menu')
async def main_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(text=skb.selectors_text['main'],
                                  reply_markup=await btni_static(data=skb.main_menu,
                                                                 adjust=1))

@router.callback_query(F.data == 'main_menu_tasks')
async def main_menu_tasks(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(text=skb.selectors_text['main'],
                                     reply_markup=await btni_static(data=skb.main_menu_tasks,
                                                                    adjust=1))

@router.callback_query(F.data == 'new_task')
async def menu_new_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(BuildTask.tittle)
    await callback.message.edit_text(text=f'{skb.new_task_intro}\n\n[TASK] Введите название задачи')

@router.callback_query(F.data == 'my_tasks')
async def menu_my_tasks(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SelectTask.selector1)
    data = await get_active_tasks(callback.message.chat.id)
    if data is None:
        await callback.message.edit_text(text='У тебя нет активных задач',
                                         reply_markup=await btni_static(data=skb.main_menu_tasks,
                                                                        adjust=1))
    else:
        mrk = genmarkup(data)
        await callback.message.edit_text(text='Список твоих активных задач', reply_markup=mrk)