# filters.py

# Встроенные модули

# Сторонние модули
from aiogram import types, Bot
from aiogram.filters import Filter
from sqlalchemy.ext.asyncio import AsyncSession

# Созданные модули
from vars_init import config

# Пример фильтра
"""
class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list) -> None:
        self.chat_types = chat_types

    async def __call__(self, msg: Union[types.Message, types.CallbackQuery]) -> bool:
        if type(msg) == types.Message:
            return msg.chat.type in self.chat_types
        
        elif type(msg) == types.CallbackQuery:
            return msg.message.chat.type in self.chat_types
"""