# user.py

# Встроенные модули

# Сторонние модули
from aiogram import Bot, F, Dispatcher, types
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession


# Созданные модули


# ------------------------ handlers ------------------------

async def start_handler(message: types.Message):
    # Приветственное сообщение и инструкция
    await message.answer(
        "<i>Здравствуйте!</i>\n\n"
        "Я <b>СКИТ help бот</b>, опишите свою проблему, и я постараюсь помочь.\n\n"
        "▫Напишите подробно, чтобы я мог быстрее разобраться в вашем вопросе."
    )


####################  Регистрируем хендлеры юзера  ####################


def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, CommandStart())
