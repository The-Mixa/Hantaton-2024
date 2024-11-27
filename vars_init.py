# vars_init.py

# Встроенные модули
import os
from environs import Env

# Загружаем переменные окружения
class ConfigManager:
    def __init__(self):
        # Инициализация переменных класса
    
        self.BOT_TOKEN = None
        self.DB_CONN_STRING = None
        self.API_URL = None
        self.API_TOKEN = None
        self.API_PASSWORD = None
        self.API_LOGIN = None
        self.AUTOUPDATE_TIME = None
        # Загрузка и валидация конфигурации
        self.init_config()

    def init_config(self):
        required_vars = [
            "BOT_TOKEN",
            "DB_CONN_STRING",
            "API_URL",
            "API_TOKEN",
            "API_LOGIN",
            "API_PASSWORD",
            "AUTOUPDATE_TIME"
        ]

        env=Env()
        env.read_env('/.env')
        
        for var in required_vars:
            value = env.str(var)
            if value is None:
                value = input(f"[.env ERROR] Enter value for {var}: ")
            # Установка значения как атрибута класса
            setattr(self, var, value)        


# Доступ к переменным
config = ConfigManager()
