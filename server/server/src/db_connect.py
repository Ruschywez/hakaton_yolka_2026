import json
from peewee import *
import os
from sys import exit

"""
    Блок является переделкой и адаптацией моего существующнего проекта:
    https://github.com/Ruschywez/warehouse-inventory-control-system.git
"""

DB_JSON = "db_parameters.json"

"""Ф-ии для работы с настройками"""
def is_json_exist():
    return os.path.isfile(DB_JSON)

def is_parameters_valid(parameters: dict) -> tuple[bool, str]:
    if parameters.get("database") == None or parameters.get("user") == None or parameters.get("password") == None or parameters.get("host") == None or parameters.get("port") == None:
        return (False, "Данные не должны быть пустые")
    if type(parameters["database"]) != str:
        return (False, f"database должно быть str! Получено: {type(parameters['database'])}")
    if type(parameters["host"]) != str:
        return (False, f"host должно быть str! Получено: {type(parameters['host'])}")
    if type(parameters["password"]) != str:
        return (False, f"password должно быть str! Получено: {type(parameters['password'])}")
    if type(parameters["port"]) != int:
        return (False, f"port должно быть int! Получено: {type(parameters['port'])}")
    if type(parameters["user"]) != str:
        return (False, f"user должно быть str! Получено: {type(parameters['user'])}")
    if len(str(parameters["port"])) != 4:
        return (False, "port должен быть 4 символа в длину!")
    # если ни одной ошибки, то...
    return (True, "")
    
def load_options() -> dict:
    """загрузка настроек"""
    try:
        with open(DB_JSON, "r", encoding="utf-8") as file:
            parameters = json.load(file)
            parameters["port"] = int(parameters["port"])
            return parameters
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка: синтаксиса в JSON: {e}")
    except ValueError:
        raise ValueError("Ошибка: 'port' должен быть числом")

def setting_parameters() -> dict:
    print("Настройка подключения к базе...")
    parameters = {}
    def input_parameters():
        parameters["host"] = input("host: ")
        parameters["port"] = int(input("port: "))
        parameters["database"] = input("database: ")
        parameters["user"] = input("user: ")
        parameters["password"] = input("password: ")
        validation = is_parameters_valid(parameters)
        if not validation[0]:
            print("Данные введены не правильно!")
            print(validation[1])
            input("Для повторного ввода нажмите Enter...")
            # Рекурсия
            input_parameters()
    input_parameters()
    print("Сохранение параметров...")
    with open(DB_JSON, "w", encoding="utf-8") as file:
        json.dump(parameters, file, indent=4, ensure_ascii=False)
    print("Параметры сохранены!")
    return parameters
"""конец блока настроек"""

def create_db_connect() -> MySQLDatabase:
    parameters = {}
    """Блок настроек"""
    if not is_json_exist():
        parameters = setting_parameters()
    else: # если файл есть
        try: # Пробуем прочесть
            if is_parameters_valid(load_options())[0]:
                parameters = load_options()
            else:
                parameters = setting_parameters()
        except Exception as e:
            """Загрузить настройки и продолжить уже с ними"""
            print(f"Ошибка при чтении файла: {e}")
            parameters = setting_parameters()
    
    """Теперь создать подключение"""
    def try_connect(params):
        try:
            db = MySQLDatabase(
                database=params.get("database"),
                user=params.get("user"),
                password=params.get("password"),
                host=params.get("host"),
                port=params.get("port"),
                autorollback=True
            )
            # Проверяем подключение
            db.connect()
            db.execute_sql('SELECT 1')
            print("Подключение к MariaDB успешно установлено!")
            return db
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            if input("Поменять настройки? [y/n]: ").lower() == "y":
                new_params = setting_parameters()
                return try_connect(new_params)
            else:
                print("Завершение работы...")
                exit(0)
    
    db = try_connect(parameters)
    if db is not None:
        return db

if __name__ == "__main__":
    db = create_db_connect()
    print(db.get_tables())