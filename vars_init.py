# vars_init.py

# Встроенные модули
import os
from dotenv import find_dotenv, load_dotenv

# Загружаем переменные окружения
class ConfigManager:
    def __init__(self):
        # Инициализация переменных класса
        self.BOT_TOKEN = None
        self.DB_SQLITE = None
        # Загрузка и валидация конфигурации
        load_dotenv(find_dotenv(filename=".env"))
        self.init_config()

    def init_config(self):
        required_vars = [
            "BOT_TOKEN",
            "DB_SQLITE",
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value is None:
                value = input(f"[.env ERROR] Enter value for {var}: ")
            # Установка значения как атрибута класса
            setattr(self, var, value)
        
        print(f"[ALL VARS COLLECTED]")


# Доступ к переменным
config = ConfigManager()
