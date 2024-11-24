# user.py

# Встроенные модули
import logging

# Сторонние модули
from aiogram import F, Dispatcher, types
from aiogram.filters import CommandStart
from nlp import get_answer

# Настроим логирование
logging.basicConfig(level=logging.INFO)

# ------------------------ handlers ------------------------

async def start_handler(message: types.Message):
    # Приветственное сообщение и инструкция
    await message.answer(
        "<i>Здравствуйте!</i>\n\n"
        "Я <b>СКИТ help бот</b>, опишите свою проблему, и я постараюсь помочь.\n\n"
        "▫️Напишите подробно, чтобы я мог быстрее разобраться в вашем вопросе."
    )


async def answer_handler(message: types.Message):
    waiting_msg = await message.answer("Ожидайте ответа...")

    try:
        question = message.text  # Получаем вопрос от пользователя
        answer_text = nlp.get_answer(question)  # Получаем ответ от NLP-системы
        try:
            await waiting_msg.delete()
        except Exception as e:
            logging.error(f"Error while deleting waiting message: {e}")
        markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Удовлетворяет", callback_data=f"answer_yes_{message.message_id}"),
             types.InlineKeyboardButton(text="Не удовлетворяет", callback_data=f"answer_no_{message.message_id}")]
        ])
        await message.answer(answer_text, reply_markup=markup)

    except Exception as e:
        await waiting_msg.delete()
        logging.error(f"Error occurred while processing the request: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.")


####################  Регистрируем хендлеры юзера  ####################

def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, CommandStart())  # Хендлер для /start
    dp.message.register(answer_handler, F.text)  # Хендлер для всех текстовых сообщений