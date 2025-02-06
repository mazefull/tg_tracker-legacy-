"""
Для параллельного исполнения процессов в ботах можно использовать асинхронные таски.
Пример:

async def bot_run():
    await dp.start_polling(bot)


async def main():
    task_pre_run = asyncio.create_task(on_timer_deadline_checker())
    task_main_bot = asyncio.create_task(bot_run())

"""


import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from dotenv import load_dotenv
import os, requests
from datetime import datetime
from datetime import timedelta
from time import sleep
from tracker.service import taskdata, notifys
from keyboard.builder import btni
from uuid import uuid4


deadline_reminder = False

stage = {
    True: 'ONLINE',
    False: 'OFFLINE'

}

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)

async def send_notify(chat_id, text, reply_marlup=None, parse_mode='HTML'):
    if await check_availability(chat_id):
        print(f'[NOTIFY] Available')
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_marlup, parse_mode=parse_mode)
    else:
        print(f'[NOTIFY] ERROR')
        return False

async def check_availability(chat_id):
    dats = requests.get(f"https://api.telegram.org/bot{TOKEN}/sendChatAction?chat_id={chat_id}&action=typing")
    if dats.status_code != 200:
        print(f'[USRCHECK][{chat_id}] ERR{dats.status_code}({(dats.json())["description"]})')
        return False
    else:
        return True


async def checker_send(specs=None):
    expiration_chart = await taskdata().get_tasks_dd()
    sprint = 3, 1
    current_date = datetime.today()
    # print(f'[CURRENT DATE] {current_date}')
    for_notify = []
    if expiration_chart is not None:
        for task in expiration_chart:
            date_for_check = datetime.strptime(task[1], '%Y-%m-%d')
            diff = date_for_check - current_date
            # print(f'{diff} for task_{task[0]}')
            if diff < timedelta(days=sprint[0]):
                for_notify.append((task, str(diff).split('.')[0]))
        # print(for_notify)


        for notify in for_notify:
            if notify[0][2] is None:
                if deadline_reminder:
                    await send_notify(chat_id=notify[0][3],
                                      text=f'Приближается дедлайн по твоей задаче {notify[0][0]}\n\nОсталось времени: {notify[1]}',
                                      reply_marlup=await btni('Открыть задачу', 'REQ_FROM_NOTIFY'))
                    await notifys().fix_last_notify(notify[0][0], str(datetime.now().strftime('%Y-%m-%d')))

            else:
                last_notify = datetime.strptime(notify[0][2], '%Y-%m-%d')
                diff_notify = datetime.today() - last_notify
                if diff_notify > timedelta(days=sprint[1]):
                    if deadline_reminder:
                        print(f'Приближается дедлайн по твоей задаче {notify[0][0]}\nОсталось времени: {notify[1]}')
                        await send_notify(chat_id=notify[0][3],
                                          text=f'Приближается дедлайн по твоей задаче {notify[0][0]}\n\nОсталось времени: {notify[1]}')


async def on_timer_deadline_checker(delay=16,  enabled=False):
    """
    Функция автоматического опроса дедлайнов через заданный промежуток времени.

    :param enabled: enabled on default.
    :param delay: delay in hours. default is 16 hours
    :return:
    """
    while enabled is True:
        print('[DD] CHECKING DEADLINE')
        print('[DD] NEED TO FIX DB_DATE >> DB_DATE_TIME  TO CORRECT LT_DIFF CHECK')
        print(f'[DD][REMINDER][STATUS] {stage[deadline_reminder]}')
        now = datetime.now()
        last_time = await notifys().get_last_timer(str(now.strftime('%Y-%m-%d')))
        if last_time is None:
            notifys().fix_last_timer(now)
            await checker_send()
        else:
            last_time = datetime.strptime(last_time, '%Y-%m-%d')
            diff_timer = now - last_time
            print('[DD][LT_DIFF] ', diff_timer)
            print('[DD][NT] ', now.strftime('%Y-%m-%d'))
            if diff_timer > timedelta(hours=16):
                notifys().fix_last_timer(now.strftime('%Y-%m-%d'))
                await checker_send()
        print(f'[DD] DONE, sleep for {delay} hours')
        await asyncio.sleep(delay*3600)


async def check_call_later():
    while True:
        print('3: ', datetime.now())
        await asyncio.sleep(5)
    # asyncio.get_event_loop().call_later(5, await on_timer_deadline_checker())


async def sync_notify_buffer(delay=20, enabled=True):
    while enabled is True:


        await asyncio.sleep(delay)