# engine.py

# Модули по умолчанию
import os

# Сторонние модули
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

# Мои модули
from . import models
from vars_init import config

# Подключение SQLite
engine = create_async_engine(config.DB_CONN_STRING)

session_maker = async_sessionmaker(
    bind = engine, class_ = AsyncSession, expire_on_commit = False
)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
