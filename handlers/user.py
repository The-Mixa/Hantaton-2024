import logging
from aiogram import F, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.filters.state import StateFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router
from api.skitAPI import SkitApi
from api.user_functions import login_user, add_user, is_login
import nlp

questionnaire_router = Router()
logging.basicConfig(level=logging.INFO)


# Определение состояний FSM
class LoginForm(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


# Хендлер для /start
@questionnaire_router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    logging.info(f"start_handler called for user {message.from_user.id}")
    tgid = message.from_user.id
    if await is_login(tgid):
        # Если пользователь авторизован, выводим меню с возможностью оставить заявку и посмотреть свои заявки
        markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Оставить заявку", callback_data="leave_request")],
            [types.InlineKeyboardButton(text="Мои заявки", callback_data="my_requests")]
        ])
        await message.answer(
            "<i>Здравствуйте!</i>\n\n"
            "Вы уже авторизованы. Можете оставить заявку или посмотреть свои заявки.",
            reply_markup=markup
        )
    else:
        await message.answer(
            "<i>Здравствуйте!</i>\n\n"
            "Я <b>СКИТ help бот</b>, опишите свою проблему, и я постараюсь помочь.\n\n"
            "▫️Напишите подробно, чтобы я мог быстрее разобраться в вашем вопросе."
        )



# Хендлер для /login
@questionnaire_router.message(CommandStart("login"))
async def login_command_handler(message: types.Message, state: FSMContext):
    logging.info(f"login_command_handler called for user {message.from_user.id}")
    tgid = message.from_user.id
    if await is_login(tgid):
        await message.answer(
            "Вы уже авторизованы. Можете оставить заявку или задать вопрос."
        )
        return
    await message.answer("Пожалуйста, введите ваш логин:")
    await state.set_state(LoginForm.waiting_for_login)


@questionnaire_router.message(StateFilter(LoginForm.waiting_for_login))
async def login_handler(message: types.Message, state: FSMContext):
    logging.info(f"login_handler called with login: {message.text}")
    tgid = message.from_user.id
    if await is_login(tgid):
        await message.answer("Вы уже авторизованы. Можете оставить заявку или задать вопрос.")
        return
    await state.update_data(login=message.text)
    back_button = InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_main_menu")
    markup = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    await message.answer("Теперь введите ваш пароль:", reply_markup=markup)
    await state.set_state(LoginForm.waiting_for_password)


@questionnaire_router.callback_query(F.data == "leave_request")
async def leave_request_handler(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info(f"Пользователь {callback_query.from_user.id} нажал 'Оставить заявку'")

    tgid = callback_query.from_user.id
    if not await is_login(tgid):
        await callback_query.answer("Для подачи заявки нужно авторизоваться.")
        await callback_query.message.answer("Пожалуйста, введите ваш логин:")
        await state.set_state(LoginForm.waiting_for_login)
        return

    back_button = InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_main_menu")

    markup = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    await state.set_state("waiting_for_application_name")
    await callback_query.message.answer("Пожалуйста, введите название вашей заявки:", reply_markup=markup)


# Хендлер для кнопки "Назад" — возвращает в главное меню
@questionnaire_router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu_handler(callback_query: types.CallbackQuery, state: FSMContext):
    tgid = callback_query.from_user.id
    logging.info(f"Пользователь {tgid} нажал 'Назад' и возвращается в главное меню.")

    await state.clear()

    await callback_query.message.delete_reply_markup()

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оставить заявку", callback_data="leave_request")],
        [InlineKeyboardButton(text="Мои заявки", callback_data="my_requests")]
    ])

    await callback_query.message.answer("Вы вернулись в главное меню. Выберите действие:", reply_markup=markup)


@questionnaire_router.message(StateFilter("waiting_for_application_content"))
async def application_content_handler(message: types.Message, state: FSMContext):
    logging.info(f"Пользователь {message.from_user.id} указал описание заявки: {message.text}")
    user_data = await state.get_data()
    application_name = user_data.get("application_name")
    application_content = message.text

    await state.update_data(application_name=application_name, application_content=application_content)

    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Подтвердить", callback_data="confirm_application")],
        [types.InlineKeyboardButton(text="Не подтверждать", callback_data="reject_application")]
    ])

    await message.answer(
        f"Почти готово!\n\n"
        f"<b>Название заявки:</b> {application_name}\n"
        f"<b>Описание заявки:</b> {application_content}\n\n"
        "Пожалуйста, подтвердите правильность заявки.",
        reply_markup=markup
    )


@questionnaire_router.callback_query(F.data == "my_requests")
async def my_requests_handler(callback_query: types.CallbackQuery, state: FSMContext):
    tgid = callback_query.from_user.id
    if await is_login(tgid):  # Проверяем авторизацию
        try:
            # Получаем заявки пользователя
            applications = await SkitApi.get_applications(tgid)

            if applications:
                text = "Ваши заявки:\n"

                inline_buttons = [
                    [InlineKeyboardButton(text=f"{app_name}", callback_data=f"view_application_{app_id}")]
                    for app_name, app_id in applications
                ]

                back_button = InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_main_menu")
                inline_buttons.append([back_button])  # Исправлено добавление кнопки в список

                markup = InlineKeyboardMarkup(inline_keyboard=inline_buttons)

                await callback_query.message.answer(text, reply_markup=markup)
            else:
                await callback_query.message.answer("У вас нет заявок.")
        except Exception as e:
            logging.error(f"Ошибка при получении заявок: {e}")
            await callback_query.message.answer("Произошла ошибка при получении ваших заявок. Попробуйте позже.")
    else:
        await callback_query.answer("Для просмотра заявок нужно авторизоваться.")
        await callback_query.message.answer("Пожалуйста, введите ваш логин.")
        await state.set_state(LoginForm.waiting_for_login)


@questionnaire_router.callback_query(F.data.startswith("view_application_"))
async def get_application_by_id(callback_query: types.CallbackQuery, state: FSMContext):
    app_id = int(callback_query.data.split("_")[2])
    try:
        # Получаем информацию о заявке по ID
        application_details = await SkitApi.get_application_by_id(app_id)
        back_button = InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_main_menu")
        markup = InlineKeyboardMarkup(inline_keyboard=[[back_button]])
        await callback_query.message.answer(application_details, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        logging.error(f"Ошибка при получении данных заявки: {e}")
        await callback_query.message.answer("Произошла ошибка при получении данных заявки. Попробуйте позже.")


@questionnaire_router.callback_query(F.data == "confirm_application")
async def confirm_application_handler(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info(f"Пользователь {callback_query.from_user.id} подтвердил заявку.")

    user_data = await state.get_data()
    application_name = user_data.get("application_name")
    application_content = user_data.get("application_content")
    tgid = callback_query.from_user.id

    try:
        await SkitApi.make_application(name=application_name, content=application_content, tgid=tgid)
        await callback_query.answer("✅Заявка успешно подтверждена и отправлена!")
        await callback_query.message.answer(
            "Заявка отправлена!"
        )
        await callback_query.message.delete_reply_markup()
    except Exception as e:
        logging.error(f"Ошибка при отправке заявки: {e}")
        await callback_query.answer("Произошла ошибка при отправке заявки. Попробуйте позже.")
        await callback_query.message.delete_reply_markup()
    finally:
        await state.clear()


@questionnaire_router.callback_query(F.data == "reject_application")
async def reject_application_handler(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info(f"Пользователь {callback_query.from_user.id} отклонил заявку.")

    await callback_query.message.delete_reply_markup()

    back_button = InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_main_menu")
    markup = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    await callback_query.message.answer("Пожалуйста, введите название новой заявки.", reply_markup=markup)
    await state.set_state("waiting_for_application_name")


@questionnaire_router.message(StateFilter("waiting_for_application_name"))
async def application_name_handler(message: types.Message, state: FSMContext):
    logging.info(f"Пользователь {message.from_user.id} указал новое название заявки: {message.text}")

    await state.update_data(application_name=message.text)

    back_button = InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_main_menu")
    markup = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    await message.answer("Теперь, пожалуйста, введите описание вашей заявки.", reply_markup=markup)
    await state.set_state("waiting_for_application_content")


@questionnaire_router.message(StateFilter(LoginForm.waiting_for_password))
async def password_handler(message: types.Message, state: FSMContext):
    logging.info(f"password_handler вызван с паролем: {message.text}")
    user_data = await state.get_data()
    id_user, login, password = message.from_user.id, user_data.get('login'), message.text

    add_user_status = await add_user(tgid=id_user)
    if add_user_status:
        logging.info(f"Пользователь {id_user} успешно добавлен!")
    else:
        logging.info(f"Пользователь {id_user} уже добавлен!")
    is_valid = await login_user(tgid=id_user, login=login, password=password)
    try:
        if is_valid:
            markup = types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text="Оставить заявку", callback_data="leave_request")]]
            )
            await message.answer("Вы успешно авторизовались! Теперь вы можете оставить заявку.", reply_markup=markup)
            await state.clear()
        else:
            await message.answer("❗Неверный логин или пароль. Попробуйте снова.\nВведите логин:")
            await state.set_state(LoginForm.waiting_for_login)
    except Exception as e:
        logging.error(f"Error occurred while processing login: {e}")
        await message.answer("❌Произошла ошибка при авторизации. Попробуйте позже.")
        await state.clear()


@questionnaire_router.message(StateFilter(None))  # Хендлер для всех сообщений, не связанных с FSM
async def answer_handler(message: types.Message, state: FSMContext):
    logging.info(f"answer_handler called with message: {message.text}")

    tgid = message.from_user.id
    # Здесь разрешаем задавать вопросы даже неавторизованным пользователям
    if not await is_login(tgid):
        logging.info(f"User {tgid} is not logged in, but they can still ask questions.")
        # Сообщаем, что пользователь не авторизован, но его вопрос будет принят
    else:
        logging.info(f"User {tgid} is logged in and is asking a question.")

    waiting_msg = await message.answer("Ожидайте ответа...\nЭто займёт примерно минуту🔍")

    try:
        question = message.text
        # Получаем категорию и текст ответа

        answer_category, answer_text = await nlp.get_answer(tgid, question)

        # Формируем текст ответа
        formatted_answer = f"*Категория:* {answer_category}\n\n*Ответ:* {answer_text}"

        markup = types.InlineKeyboardMarkup(inline_keyboard=[[  # Создание кнопок для ответа
            types.InlineKeyboardButton(text="Удовлетворяет", callback_data=f"answer_yes_{message.message_id}"),
            types.InlineKeyboardButton(text="Не удовлетворяет", callback_data=f"answer_no_{message.message_id}")
        ]])
        
        logging.info(f"Sending answer with inline buttons: answer_yes_{message.message_id}, answer_no_{message.message_id}")
        
        await waiting_msg.delete()  # Удаляем сообщение ожидания
        # Отправляем ответ с кнопками  
        await message.answer(formatted_answer, reply_markup=markup, parse_mode="Markdown")

    except Exception as e:
        try:
            await waiting_msg.delete()
        except Exception as delete_error:
            logging.warning(f"Message to delete not found or already deleted: {delete_error}")

        logging.error(f"Error occurred while processing the request: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.")



@questionnaire_router.callback_query(F.data)
async def answer_no_handler(callback_query: types.CallbackQuery, state: FSMContext):
    tgid = callback_query.from_user.id
    if "answer_yes" in callback_query.data:
        await callback_query.message.answer("Отлично! Был рад помочь!")
    # Проверяем, авторизован ли пользователь
    elif await is_login(tgid):
        logging.info(f"User {tgid} clicked 'Не удовлетворяет' and is logged in.")
        await callback_query.answer("Давайте создадим заявку.")
        back_button = InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_main_menu")
        markup = InlineKeyboardMarkup(inline_keyboard=[[back_button]])
        await callback_query.message.answer("Пожалуйста, введите название вашей заявки.", reply_markup=markup)
        await state.set_state("waiting_for_application_name")
    else:
        # Если не авторизован, запрашиваем логин
        logging.info(f"User {tgid} clicked 'Не удовлетворяет' but is not logged in.")
        await callback_query.answer("Давайте авторизуемся, чтобы перейти к оформлению заявки.")
        await state.set_state(LoginForm.waiting_for_login)
        await callback_query.message.answer("Пожалуйста, введите ваш логин.")


def register_handlers(dp: Dispatcher):
    logging.info("Registering handlers...")
    dp.include_router(questionnaire_router)  # Регистрация маршрутов
