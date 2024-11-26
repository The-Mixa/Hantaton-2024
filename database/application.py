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
        self.CREATED = 1
        self.WORK_IN_PROGRESS = 2
        self.CORRECTION = 4
        self.DONE = 5
        self.CLOSE = 6
        self.AGGREMENT = 10

        self.enscriptons = {
            1: 'Создана', 
            2: 'В работе',
            4: 'Уточнение у инициатора',
            5: 'Решена',
            6: 'Закрыта',
            10: 'В ожидании согласования'            
        }

statuses = ApplicationStatuses()


class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_time = Column(DateTime, default=dt.now())
    status = Column(Integer, default=statuses.CREATED)
    user_tgid = Column(Integer, ForeignKey('users.tgid'))

    user = relationship('User')




