# main.py

# Встроенные модули
import asyncio
import os
from datetime import datetime
import logging
# Сторонние модули
from aiogram import Bot, Dispatcher, types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import time

# Созданные модули
from handlers import user, admin
from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from commands import admin_commands, user_commands
from vars_init import config
from api.skitAPI import api, connection, statuses, application_solution_format
from database.application import Application
from database.user import User

bot = Bot(
    token=config.BOT_TOKEN, parse_mode="HTML",
    disable_web_page_preview=True
)

dp = Dispatcher()


@connection
async def applications_autoupdations(session: AsyncSession) -> None:
    while True:

        users_result = await session.execute(select(User))
        users: List[User] = list(users_result.scalars())

        for user in users:
            applications_result = await session.execute(select(Application).where(Application.user_tgid == user.tgid))
            applications: List[Application] = list(applications_result.scalars())

            for application in applications:
                data = await api.get_application(application.id)
                if data['status'] != application.status and data['status'] == statuses.DONE:
                    answer = await application_solution_format(int(user.tgid), data)
                    await bot.send_message(int(user.tgid), answer)
                    application.status = statuses.DONE
                    await session.commit()

        await asyncio.sleep(int(config.AUTOUPDATE_TIME))


async def on_startup():
    run_param = False  # Заменяем на True, если надо дропнуть БД
    logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w")
    if run_param:
        await drop_db()
    await create_db()

    admin.register_handlers(dp)
    user.register_handlers(dp)


async def main():
    dp.startup.register(on_startup)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)

    await bot.set_my_commands(admin_commands, scope=types.BotCommandScopeAllGroupChats())
    await bot.set_my_commands(user_commands, scope=types.BotCommandScopeAllPrivateChats())

    time_now = datetime.today()
    print(f"[{str(time_now)[:19]}]: Bot started")

    await asyncio.gather( dp.start_polling(bot), applications_autoupdations())


# Запуск бота
if __name__ == "__main__":
    try:
        # Чтобы не было ошибки RuntimeError
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())

    except KeyboardInterrupt:
        print("Bot stopped")

