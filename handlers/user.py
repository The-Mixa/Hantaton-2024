import logging
from aiogram import F, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.filters.state import StateFilter
from aiogram import Router
import nlp

questionnaire_router = Router()
logging.basicConfig(level=logging.INFO)


# Определение состояний FSM
class LoginForm(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


# Хендлер для /start
@questionnaire_router.message(CommandStart())
async def start_handler(message: types.Message):
    logging.info(f"start_handler called for user {message.from_user.id}")
    await message.answer(
        "<i>Здравствуйте!</i>\n\n"
        "Я <b>СКИТ help бот</b>, опишите свою проблему, и я постараюсь помочь.\n\n"
        "▫️Напишите подробно, чтобы я мог быстрее разобраться в вашем вопросе."
    )


# Хендлер для /login
@questionnaire_router.message(CommandStart("login"))
async def login_command_handler(message: types.Message, state: FSMContext):
    logging.info(f"login_command_handler called for user {message.from_user.id}")

    # Запускаем процесс авторизации
    await message.answer("Пожалуйста, введите ваш логин.")
    await state.set_state(LoginForm.waiting_for_login)


# Хендлер для ответа на вопрос пользователя (не касается логина/пароля)
@questionnaire_router.message(StateFilter(LoginForm.waiting_for_login))
async def login_handler(message: types.Message, state: FSMContext):
    logging.info(f"login_handler called with login: {message.text}")
    await state.update_data(login=message.text)

    await message.answer("Теперь введите ваш пароль.")
    await state.set_state(LoginForm.waiting_for_password)


@questionnaire_router.message(StateFilter(LoginForm.waiting_for_password))
async def password_handler(message: types.Message, state: FSMContext):
    logging.info(f"password_handler called with password: {message.text}")
    user_data = await state.get_data()
    login = user_data.get('login')
    password = message.text
    await message.answer("Вы успешно авторизовались!")
    await state.clear()


# Хендлер для обычных сообщений пользователя (вне процесса авторизации)
@questionnaire_router.message(StateFilter(None))  # Фильтрует все сообщения, не касающиеся FSM
async def answer_handler(message: types.Message):
    logging.info(f"answer_handler called with message: {message.text}")
    waiting_msg = await message.answer("Ожидайте ответа...")

    try:
        question = message.text
        answer_text = nlp.get_answer(question)

        await waiting_msg.delete()

        markup = types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(text="Удовлетворяет", callback_data=f"answer_yes_{message.message_id}"),
            types.InlineKeyboardButton(text="Не удовлетворяет", callback_data=f"answer_no_{message.message_id}")
        ]])

        logging.info(
            f"Sending answer with inline buttons: answer_yes_{message.message_id}, answer_no_{message.message_id}")
        await message.answer(answer_text, reply_markup=markup)

    except Exception as e:
        await waiting_msg.delete()
        logging.error(f"Error occurred while processing the request: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.")


# Хендлер для кнопки "Не удовлетворяет"
@questionnaire_router.callback_query(F.data)
async def answer_no_handler(callback_query: types.CallbackQuery, state: FSMContext):
    if "answer_no" in callback_query.data:
        await callback_query.answer("Давайте авторизуемся, чтобы перейти к оформлению заявки.")
        await state.set_state(LoginForm.waiting_for_login)
        await callback_query.message.answer("Пожалуйста, введите ваш логин.")
    if "answer_yes" in callback_query.data:
        logging.info(f"User {callback_query.from_user.id} clicked 'Удовлетворяет'")
        await callback_query.answer("Спасибо, что подтвердили, что ответ вам подходит!")
        await callback_query.message.answer(
            "Рад, что смог помочь! Если у вас возникнут другие вопросы, не стесняйтесь обращаться."
        )
        await callback_query.message.delete_reply_markup()


def register_handlers(dp: Dispatcher):
    logging.info("Registering handlers...")
    dp.include_router(questionnaire_router)  # Регистрация маршрутов
    
