# inline.py

# Модули по умолчанию
from typing import Dict, Tuple, List

# Сторонние модули
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


# Метод генерации inline кнопок
def gen_inline_keyboard(
        buttons: Dict[str, str],  # Словарь в котором ключ – text inline кнопки, а значение – callback_data
        size: Tuple[int] = (1,)  # Как должны быть расположены кнопки(по умолчанию 1 в ряд)
) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardBuilder()

    for text, call_data in buttons.items():
        keyboard.add(
            InlineKeyboardButton(
                text = text, callback_data = call_data
            )
        )

    return keyboard.adjust(*size).as_markup()

# Метод генерации inline кнопок со ссылками
def gen_inline_links_keyboard(
        buttons: Dict[str, str],  # Словарь в котором ключ – text inline кнопки, а значение – url
        size: Tuple[int] = (1,)  # Как должны быть расположены кнопки(по умолчанию 1 в ряд)
) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardBuilder()

    for text, url in buttons.items():
        keyboard.add(
            InlineKeyboardButton(
                text = text, url = url
            )
        )

    return keyboard.adjust(*size).as_markup()

# Метод генерации смешанной инлайн клавиатуры в котором и url, и callback_data 
def gen_inline_mix_keyboard(
        buttons: Dict[str, str],  # Словарь в котором есть и callback, и url inline кнопки
        size: Tuple[int] = (1,)  # Как должны быть расположены кнопки(по умолчанию 1 в ряд) 
) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardBuilder()

    for text, value in buttons.items():
        if "://" in value:  # Если ссылка
            keyboard.add(
                InlineKeyboardButton(
                    text = text, url = value
                )
            )

        else:
            keyboard.add(
                InlineKeyboardButton(
                    text = text, callback_data = value
                )
            )

    return keyboard.adjust(*size).as_markup()

# Создаём класс пагинации, который наследует объект CallbackData
class Pagination(CallbackData, prefix = "pag"):
    action: str
    page: int

def gen_pagination_keyboard(
        prev_name: str,  # Название действия, которое покажет предыдущую страницу
        next_name: str,  # Название действия, которое покажет следующую страницу
        buttons: Dict[str, str],  # Словарь, в котором ключ – text inline кнопки, а значение – callback_data
        size: Tuple[int] = (1,),  # Как должны быть расположены кнопки(по умолчанию 1 в ряд)
        current_page: int = 0,  # Текущая страница пагинации
        first_page: int = 0,  # Первая страница пагинации
        last_page: int = 0  # Последняя страница пагинации
) -> InlineKeyboardMarkup:
    
    keyboard = InlineKeyboardBuilder()

    for text, call_data in buttons.items():
        keyboard.add(
            InlineKeyboardButton(
                text = text, callback_data = call_data
            )
        )

    keyboard.adjust(*size)

    pages_buttons = []  # Кнопки перелистывания страниц пагинации

    prev_btn = InlineKeyboardButton(
        text = "⬅️",
        callback_data = Pagination(action = prev_name, page = current_page).pack()
    )

    next_btn = InlineKeyboardButton(
        text = "➡️",
        callback_data = Pagination(action = next_name, page = current_page).pack()
    )

    # Если только одна страница, то не отображать кнопки prev и next
    if first_page == last_page:
        return keyboard.as_markup()

    # Если первая страница, то отображать только кнопку next
    if current_page == 0:
        pages_buttons.append(next_btn)

    # Если последняя страница, то отображать только кнопку prev
    elif current_page == last_page:
        pages_buttons.append(prev_btn)

    else:
        pages_buttons.extend([prev_btn, next_btn])

    return keyboard.row(*pages_buttons).as_markup()
