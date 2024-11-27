# user_functions.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

#  мои модули
from middlewares.db import DataBaseSession
from database.engine import session_maker
from database.application import Application
from database.user import User
from database.engine import connection
from api.skitAPI import SkitApi
from vars_init import config


# Добавление пользователя с tgid в базу данных
@connection
async def add_user(tgid: str, session: AsyncSession) -> bool:
    result = await session.execute(select(User).where(User.tgid == tgid))
    users = list(result.scalars())
    if users:
        return False
    
    user = User(tgid=tgid)
    session.add(user)
    await session.commit()

    return True


# Проверка пользователя с tgid на то, указывал ли он когда либо пароль
@connection
async def is_login(tgid: str, session: AsyncSession) -> bool:
    result = await session.execute(select(User).where(User.tgid == tgid))
    users = list(result.scalars())

    if not users:
        return False
    return users[0].is_login


# добавление логина и пароля в СКИТ к указанному tgid
@connection
async def login_user(tgid: str, login: str, password: str, session: AsyncSession) -> bool:
    result = await session.execute(select(User).where(User.tgid == tgid))
    user = list(result.scalars())[0]
    user.login = login
    user.password = password
    await session.commit()
    if await SkitApi.make_session(tgid=tgid):
        result = await session.execute(select(User).where(User.tgid == tgid))
        user = list(result.scalars())[0]
        
        user.is_login = True
        await session.commit()
        
        return True
    return False


