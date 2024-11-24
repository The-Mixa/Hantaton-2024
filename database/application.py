# applications.py

from datetime import datetime as dt


# Сторонние модули
from sqlalchemy import (
    Integer, String, Text, DateTime, Date,
    ForeignKey, Boolean, func,
    Column
)

from sqlalchemy.orm import (relationship)

from .models import Base


class ApplicationStatuses:
    def __init__(self):
        self.CREATED = 0
        self.DONE = 1


statuses = ApplicationStatuses()


class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_time = Column(DateTime, default=dt.now())
    status = Column(Integer, default=statuses.CREATED)
    user_tgid = Column(Integer, ForeignKey('users.tgid'))

    user = relationship('User')


