from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router
from aiogram.filters import Command
import logging
from aiogram import F, Dispatcher, types
from api.skitAPI import SkitApi
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from middlewares.db import DataBaseSession

admin_router = Router()

# ID администраторов (можно загрузить из базы данных или конфигурационного файла)
ADMIN_IDS = [7447585065, 1620952084]  # Пример, замените на реальные ID


# Проверка, является ли пользователь администратором
async def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@admin_router.message(Command("admin"))
async def admin_start(message: types.Message):
    logging.info(f"User ID: {message.from_user.id}")
    if await is_admin(message.from_user.id):
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Просмотр всех заявок", callback_data="view_all_requests")],
            [InlineKeyboardButton(text="Просмотр пользователей", callback_data="delete_request")],
        ])
        logging.info("Markup prepared, sending message...")
        await message.answer("Добро пожаловать в админ-панель! Выберите действие:", reply_markup=markup)
    else:
        await message.answer("❌У вас нет прав для доступа к админ-панели")


@admin_router.callback_query(F.data == "view_all_requests")
async def view_all_requests(callback_query: types.CallbackQuery):
    if await is_admin(callback_query.from_user.id):
        try:



            ########## МИШАНЯ, СЮДА ВСТАВЛЯЙ ##########
            text = await SkitApi.get_all_applications()



            # Проверка на пустоту полученных заявок
            if text:
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
        # Если пользователь не администратор
        await callback_query.message.answer("У вас нет прав для выполнения этого действия.")


@admin_router.callback_query(F.data == "view_all_requests")
async def view_all_users(callback_query: types.CallbackQuery):
    if await is_admin(callback_query.from_user.id):
        try:



            ########## МИШАНЯ, СЮДА ВСТАВЛЯЙ ##########
            text = await SkitApi.get_all_users()



            # Проверка на пустоту полученных заявок
            if text:
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
        # Если пользователь не администратор
        await callback_query.message.answer("У вас нет прав для выполнения этого действия.")


# Хендлер для кнопки "Назад" в админ-меню
@admin_router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu(callback_query: types.CallbackQuery):
    if await is_admin(callback_query.from_user.id):
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Просмотр всех заявок", callback_data="view_all_requests")],
            [InlineKeyboardButton(text="Просмотр пользователей", callback_data="delete_request")],
            [InlineKeyboardButton(text="Вернуться в меню пользователя", callback_data="back_to_main_menu")]
        ])
        await callback_query.message.answer("Вы в административной панели. Выберите действие:", reply_markup=markup)


# Хендлер для выхода в главное меню (кнопка "Назад")
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
