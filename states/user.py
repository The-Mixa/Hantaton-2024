# user.py

# Сторонние модули
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, CallbackQuery

# Созданные модули


class States(StatesGroup):
    pass


# Метод, который сбрасывает любой стейт при нажатии на inline кнопку
async def reset_state(
        callback: CallbackQuery,
        state: FSMContext,
        message_text: str,
        keyboard: InlineKeyboardMarkup = None
):
    current_state = await state.get_state()
    if current_state is None:
        return
    else:
        await state.clear()
        await callback.message.edit_text(
            message_text, reply_markup=keyboard
        )