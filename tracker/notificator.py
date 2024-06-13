import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from dotenv import load_dotenv
import os, requests
from datetime import datetime
from datetime import timedelta
from time import sleep
from tracker.service import get_tasks_dd, fix_last_notify, get_last_timer, fix_last_timer
from keyboard.builder import btni

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)

async def send_notify(chat_id, text, reply_marlup=None):
    if await check_availability(chat_id):
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_marlup)
    else:
        print(f'[NOTIFY] ERROR')
        return False

async def check_availability(chat_id):
    dats = requests.get(f"https://api.telegram.org/bot{TOKEN}/sendChatAction?chat_id={chat_id}&action=typing")
    if dats.status_code != 200:
        print(f'[USRCHECK][{chat_id}] NA. ERRCODE: {dats.status_code}')
        return False
    else:
        return True

async def checker_send(specs=None):
    expiration_chart = await get_tasks_dd()
    sprint = 3, 1
    current_date = datetime.today()
    # print(f'[CURRENT DATE] {current_date}')
    for_notify = []
    for task in expiration_chart:
        date_for_check = datetime.strptime(task[1], '%Y-%m-%d')
        diff = date_for_check - current_date
        # print(f'{diff} for task_{task[0]}')
        if diff < timedelta(days=sprint[0]):
            for_notify.append((task, str(diff).split('.')[0]))
    # print(for_notify)

    for notify in for_notify:
        if notify[0][2] is None:
            print(f'Приближается дедлайн по твоей задаче {notify[0][0]}\n\nОсталось времени: {notify[1]}')
            await send_notify(chat_id=notify[0][3], text=f'Приближается дедлайн по твоей задаче {notify[0][0]}\n\nОсталось времени: {notify[1]}', reply_marlup=await btni('Открыть задачу', 'REQ_FROM_NOTIFY'))
            await fix_last_notify(notify[0][0], str(datetime.now().strftime('%Y-%m-%d')))
        else:
            last_notify = datetime.strptime(notify[0][2], '%Y-%m-%d')
            diff_notify = datetime.today() - last_notify
            if diff_notify > timedelta(days=sprint[1]):
                print(f'Приближается дедлайн по твоей задаче {notify[0][0]}\n\nОсталось времени: {notify[1]}')
                await send_notify(chat_id=notify[0][3], text=f'Приближается дедлайн по твоей задаче {notify[0][0]}\n\nОсталось времени: {notify[1]}')


async def on_timer_deadline_checker(delay=16,  enabled=True):
    """
    Функция автоматического опроса дедлайнов через заданный промежуток времени.

    :param enabled: enabled on default.
    :param delay: delay in hours. default is 16 hours
    :return:
    """
    while enabled is True:
        print('[DEADLINE] CHECKING DEADLINE')
        print('[DEADLINE] NEED TO FIX DB_DATE >> DB_DATE_TIME  TO CORRECT LT_DIFF CHECK')
        now = datetime.now()
        last_time = await get_last_timer(str(now.strftime('%Y-%m-%d')))
        if last_time is None:
            fix_last_timer(now)
            await checker_send()
        else:
            last_time = datetime.strptime(last_time, '%Y-%m-%d')
            diff_timer = now - last_time
            print('LT_DIFF ', diff_timer)
            print('NOW ', now.strftime('%Y-%m-%d'))
            if diff_timer > timedelta(hours=16):
                fix_last_timer(now.strftime('%Y-%m-%d'))
                await checker_send()
        print(f'[DEADLINE] DONE, sleep for {delay} hours')
        await asyncio.sleep(delay*3600)


async def check_call_later():
    while True:
        print('3: ', datetime.now())
        await asyncio.sleep(5)
    # asyncio.get_event_loop().call_later(5, await on_timer_deadline_checker())