# users.py

# Сторонние модули
from sqlalchemy import (
    Integer, String, Text, DateTime, Date,
    ForeignKey, Boolean, func,
    Column
)

from sqlalchemy.orm import (relationship)

from .models import Base


class User(Base):
    __tablename__ = 'users'

    tgid = Column(String, primary_key=True, autoincrement=True)
    is_login = Column(Boolean, default=False)
    login = Column(String, nullable=True)
    password = Column(String, nullable=True)
    
    applications = relationship('Application', back_populates='user')