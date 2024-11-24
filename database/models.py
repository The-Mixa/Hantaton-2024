# models.py

# Сторонние модули
from sqlalchemy import (
    Integer, String, Text, DateTime, Date,
    ForeignKey, Boolean, func
)

from sqlalchemy.orm import (
    DeclarativeBase, Mapped,
    mapped_column, relationship
)


# Столбцы таблицы, которые создаются автоматически
class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(
                                DateTime(timezone = True),
                                default = func.now()
                            )
    
    updated: Mapped[DateTime] = mapped_column(
                                DateTime(timezone = True),
                                default = func.now(),
                                onupdate = func.now()
                            )