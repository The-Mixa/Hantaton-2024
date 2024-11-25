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


class Base(DeclarativeBase):
    pass