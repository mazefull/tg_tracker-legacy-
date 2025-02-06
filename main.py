from aiogram import Bot, Dispatcher
import asyncio
import logging
from handlers.messages import router as m_router
from handlers.tasks import router as c_router
from handlers.commands import router as uc_router, notify_task_assigned
from handlers.informer import router as inf_router
from tracker.service import database, config, create_reg_sheet
from tracker.notificator import checker_send, on_timer_deadline_checker, check_call_later, sync_notify_buffer
from tracker.service import notifys, taskdata

from dotenv import load_dotenv
import os


pre_run = False  #Активация DEADLINE TIMER
sync_buffer = False  #Отправка уведомлений по ручным таскам из буфера

load_dotenv()
TOKEN = os.getenv("TOKEN")




notify = notifys()
taskdata = taskdata()
bot = Bot(token=TOKEN)
dp = Dispatcher()
# asyncio.run(taskdata.get_task_issuer("9931770340eb"))

async def bot_run():

    print('[BOT][POLLING][MODE]: ASYNC')
    await create_reg_sheet()
    await dp.start_polling(bot)



async def main():
    if pre_run: task_pre_run = asyncio.create_task(on_timer_deadline_checker())
    if sync_buffer: task_sync_notify_buffer = asyncio.create_task(sync_notify_buffer())
    task_main_bot = asyncio.create_task(bot_run())
    dp.include_routers(
        c_router,
        uc_router,
        m_router,
        inf_router,
    )

    if pre_run: await task_pre_run
    if sync_buffer: await task_sync_notify_buffer
    await task_main_bot


if __name__ == "__main__":
    islog = True
    if islog is True:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - [%(levelname)s] - %(name)s - "
                            "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
    else:
        pass
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("EXIT")