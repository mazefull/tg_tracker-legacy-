import datetime

from aiogram import Bot, Dispatcher
import asyncio
import logging
from handlers.messages import router as m_router
from handlers.tasks import router as c_router
from handlers.commands import router as uc_router
from tracker.service import database, config
from tracker.notificator import checker_send, on_timer_deadline_checker, check_call_later

from dotenv import load_dotenv
import os


load_dotenv()
TOKEN = os.getenv("TOKEN")


bot = Bot(token=TOKEN)
dp = Dispatcher()


async def bot_run():
    print('[BOT][POLLING][MODE]: ASYNC')
    await dp.start_polling(bot)


async def main():
    task_pre_run = asyncio.create_task(on_timer_deadline_checker())
    task_main_bot = asyncio.create_task(bot_run())


    # print('2: ', datetime.datetime.now())
    dp.include_routers(
        c_router,
        uc_router,
        m_router,
    )

    await task_pre_run
    await task_main_bot


if __name__ == "__main__":
    islog = False
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