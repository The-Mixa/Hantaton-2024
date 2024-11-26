# main.py

# Встроенные модули
import asyncio
import os
from datetime import datetime
import logging
# Сторонние модули
from aiogram import Bot, Dispatcher, types

# Созданные модули
from handlers import user, admin
from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from commands import admin_commands, user_commands
from vars_init import config
from api.skitAPI import api
from api.user_functions import login_user

bot = Bot(
    token = config.BOT_TOKEN, parse_mode = "HTML",
    disable_web_page_preview = True
)

dp = Dispatcher()

async def on_startup():
    run_param = False  # Заменяем на True, если надо дропнуть БД
    logging.basicConfig(level=logging.INFO)

    if run_param:
        await drop_db()
    await create_db()

    user.register_handlers(dp)
    admin.register_handlers(dp)


async def main():
    dp.startup.register(on_startup)
    dp.update.middleware(DataBaseSession(session_pool = session_maker))
    await bot.delete_webhook(drop_pending_updates = True)

    await bot.set_my_commands(admin_commands, scope = types.BotCommandScopeAllGroupChats())
    await bot.set_my_commands(user_commands, scope = types.BotCommandScopeAllPrivateChats())

    time_now = datetime.today()
    print(f"[{str(time_now)[:19]}]: Bot started")

    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    try:
        # Чтобы не было ошибки RuntimeError
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Bot stopped")

