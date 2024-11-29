from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router
from aiogram.filters import Command
from aiogram import F, Dispatcher, types
import logging
from api.skitAPI import api  # Предполагается, что get_all_users находится в этом файле
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from middlewares.db import DataBaseSession

admin_router = Router()

# ID администраторов
ADMIN_IDS = [7447585065, 1620952084, 1835880628]


# Проверка, является ли пользователь администратором
async def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@admin_router.message(Command("admin"))
async def admin_start(message: types.Message):
    logging.info(f"User ID: {message.from_user.id}")
    if await is_admin(message.from_user.id):
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Просмотр всех заявок", callback_data="view_all_requests")],
            [InlineKeyboardButton(text="Просмотр пользователей", callback_data="view_all_users")],
            # Кнопка для просмотра пользователей
        ])
        logging.info("Markup prepared, sending message...")
        await message.answer("Добро пожаловать в админ-панель! Выберите действие:", reply_markup=markup)
    else:
        await message.answer("❌У вас нет прав для доступа к админ-панели")


@admin_router.callback_query(F.data == "view_all_requests")
async def view_all_requests(callback_query: types.CallbackQuery):
    if await is_admin(callback_query.from_user.id):
        try:
            applications = await api.get_all_applications()
            if applications:
                text = "\n".join([f"Заявка: {app_id} - {app_info}" for app_id, app_info in applications])
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Назад", callback_data="back_to_admin_menu")]
                ])
                await callback_query.message.answer(text, parse_mode="HTML", reply_markup=markup)
            else:
                await callback_query.message.answer("Нет заявок.")
        except Exception as e:
            logging.error(f"Ошибка при получении заявок: {e}")
            await callback_query.message.answer("Произошла ошибка при получении заявок. Попробуйте позже.")
    else:
        await callback_query.message.answer("У вас нет прав для выполнения этого действия.")


@admin_router.callback_query(F.data == "view_all_users")
async def view_all_users(callback_query: types.CallbackQuery):
    if await is_admin(callback_query.from_user.id):
        try:
            # Получаем всех пользователей
            users = await api.get_all_users()

            if users:
                inline_buttons = [
                    [InlineKeyboardButton(text=f"{user_login} (ID: {tgid})", callback_data=f"user_{tgid}")]
                    for user_login, tgid in users
                ]
                inline_buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_to_admin_menu")])
                markup = InlineKeyboardMarkup(inline_keyboard=inline_buttons)
                await callback_query.message.answer("Выберите пользователя:", reply_markup=markup)
            else:
                await callback_query.message.answer("Нет пользователей.")
        except Exception as e:
            logging.error(f"Ошибка при получении пользователей: {e}")
            await callback_query.message.answer("Произошла ошибка при получении пользователей. Попробуйте позже.")
    else:
        await callback_query.message.answer("У вас нет прав для выполнения этого действия.")


@admin_router.callback_query(F.data.startswith("user_"))
async def view_user_applications(callback_query: types.CallbackQuery):
    tgid = str(callback_query.data.split("_")[1])
    try:
        # Получаем заявки пользователя
        applications = await api.get_applications(str(tgid))

        if applications:
            text = "Заявки пользователя:\n"

            inline_buttons = [
                [InlineKeyboardButton(text=f"{app_name}", callback_data=f"view_application_{app_id}")]
                for app_name, app_id in applications
            ]

            back_button = InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_main_menu")
            inline_buttons.append([back_button])  # Исправлено добавление кнопки в список

            markup = InlineKeyboardMarkup(inline_keyboard=inline_buttons)

            await callback_query.message.answer(text, reply_markup=markup)
        else:
            print(applications, tgid)
            await callback_query.message.answer("У пользователя нет заявок.")
    except Exception as e:
        logging.error(f"Ошибка при получении заявок: {e}")
        await callback_query.message.answer("Произошла ошибка при получении ваших заявок. Попробуйте позже.")


@admin_router.callback_query(F.data.startswith("view_application_"))
async def get_application_by_id(callback_query: types.CallbackQuery, state: FSMContext):
    app_id = int(callback_query.data.split("_")[2])
    try:
        # Получаем информацию о заявке по ID
        application_details = await api.get_application_by_id(app_id)
        back_button = InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_main_menu")
        markup = InlineKeyboardMarkup(inline_keyboard=[[back_button]])
        await callback_query.message.answer(application_details, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        logging.error(f"Ошибка при получении данных заявки: {e}")
        await callback_query.message.answer("Произошла ошибка при получении данных заявки. Попробуйте позже.")


@admin_router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu(callback_query: types.CallbackQuery):
    if await is_admin(callback_query.from_user.id):
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Просмотр всех заявок", callback_data="view_all_requests")],
            [InlineKeyboardButton(text="Просмотр пользователей", callback_data="view_all_users")],
            [InlineKeyboardButton(text="Вернуться в меню пользователя", callback_data="back_to_main_menu")]
        ])
        await callback_query.message.answer("Вы в административной панели. Выберите действие:", reply_markup=markup)


@admin_router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback_query: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оставить заявку", callback_data="leave_request")],
        [InlineKeyboardButton(text="Мои заявки", callback_data="my_requests")]
    ])
    await callback_query.message.answer("Вы вернулись в главное меню. Выберите действие:", reply_markup=markup)


def register_admin_handlers(dp: Dispatcher):
    logging.info("Registering admin handlers...")
    dp.include_router(admin_router)


def register_handlers(dp: Dispatcher):
    logging.info("Registering admin handlers...")
    dp.include_router(admin_router)
