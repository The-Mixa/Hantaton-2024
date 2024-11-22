# admin.py

# Встроенные модули

# Сторонние модули
from aiogram import Bot, F, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

# Созданные модули


#------------------------ handlers ------------------------


# Регистрация хэндлеров
def register_handlers(dp: Dispatcher):
    pass