from datetime import datetime
from peewee import DoesNotExist
from .entities import User, Education_level, Messages, Messages_type
from typing import List, Tuple, Optional

SYSTEM_TYPE = 1
USER_TYPE = 2
BOT_TYPE = 3

class UserRepository:
    """Репозиторий для работы с пользователями"""

    @staticmethod
    def create(login: str, password: str, last_name: str, first_name: str,
               surname: str, date_birth: str = None, education_level: str = None,
               education_specialize: str = None, interests: str = None) -> int:
        """Создание нового пользователя"""
        user_data = {
            "login": login,
            "password": password,
            "last_name": last_name,
            "first_name": first_name,
            "surname": surname,
        }

        if education_level is not None and education_level.strip():
            try:
                edu_level_obj = Education_level.get(Education_level.name == education_level)
                user_data["education_level"] = edu_level_obj.level
            except DoesNotExist:
                raise ValueError(f"Уровень образования '{education_level}' не найден")
        else:
            user_data["education_level"] = None

        if education_specialize is not None:
            user_data["education_specialize"] = education_specialize
        if interests is not None:
            user_data["interests"] = interests
        if date_birth is not None:
            user_data["date_birth"] = date_birth

        user = User.create(**user_data)
        return user.user

    @staticmethod
    def get_by_login_password(login: str, password: str) -> Optional[int]:
        """Получение user_id по логину и паролю"""
        try:
            user = User.get((User.login == login) & (User.password == password))
            return user.user
        except DoesNotExist:
            return None

    @staticmethod
    def get_by_id(user_id: int) -> Optional[dict]:
        """Получение полного профиля пользователя по ID"""
        try:
            user = User.get(User.user == user_id)
            return user.to_dict()
        except DoesNotExist:
            return None

    @staticmethod
    def update(user_id: int, **kwargs) -> bool:
        """Обновление данных пользователя"""
        try:
            user = User.get(User.user == user_id)

            if "education_level" in kwargs and kwargs["education_level"] is not None:
                try:
                    edu_level_obj = Education_level.get(Education_level.name == kwargs["education_level"])
                    kwargs["education_level"] = edu_level_obj.level
                except DoesNotExist:
                    raise ValueError(f"Уровень образования '{kwargs['education_level']}' не найден")

            for key, value in kwargs.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            user.save()
            return True
        except DoesNotExist:
            return False

    @staticmethod
    def delete(user_id: int) -> bool:
        """Удаление пользователя"""
        try:
            user = User.get(User.user == user_id)
            user.delete_instance()
            return True
        except DoesNotExist:
            return False


class MessagesRepository:
    """Репозиторий для работы с сообщениями"""

    @staticmethod
    def get_by_user(user_id: int) -> List[Tuple[int, str, str, datetime]]:
        """Получение всех сообщений пользователя"""
        messages = (Messages
                   .select()
                   .where(Messages.user == user_id)
                   .order_by(Messages.date_time.desc()))

        return [(msg.message, msg.text, msg.type.name, msg.date_time)
                for msg in messages]

    @staticmethod
    def get_history_for_ai(user_id: int) -> List[dict]:
        """Получение истории сообщений для контекста GigaChat"""
        messages = (Messages
                   .select()
                   .where(Messages.user == user_id)
                   .order_by(Messages.date_time.asc()))

        history = []
        for msg in messages:
            role = "assistant" if msg.type.type == BOT_TYPE else "user"
            history.append({"role": role, "content": msg.text})
        return history

    @staticmethod
    def create(user_id: int, text: str, message_type: int = USER_TYPE) -> bool:
        """Создание нового сообщения"""
        try:
            # Проверяем существует ли пользователь
            User.get(User.user == user_id)

            Messages.create(
                user=user_id,
                type=message_type,
                text=text,
                date_time=datetime.now()
            )
            return True
        except DoesNotExist:
            return False

    @staticmethod
    def update(message_id: int, text: str) -> bool:
        """Обновление текста сообщения"""
        try:
            message = Messages.get(Messages.message == message_id)
            message.text = text
            message.save()
            return True
        except DoesNotExist:
            return False

    @staticmethod
    def delete(message_id: int) -> bool:
        """Удаление сообщения"""
        try:
            message = Messages.get(Messages.message == message_id)
            message.delete_instance()
            return True
        except DoesNotExist:
            return False


class EducationLevelRepository:
    """Репозиторий для работы с уровнями образования (вспомогательный)"""

    @staticmethod
    def get_all() -> List[dict]:
        """Получение всех уровней образования"""
        levels = Education_level.select()
        return [level.to_dict() for level in levels]

    @staticmethod
    def get_by_id(level_id: int) -> Optional[dict]:
        """Получение уровня образования по ID"""
        try:
            level = Education_level.get(Education_level.level == level_id)
            return level.to_dict()
        except DoesNotExist:
            return None

    @staticmethod
    def get_by_name(name: str) -> Optional[dict]:
        """Получение уровня образования по названию"""
        try:
            level = Education_level.get(Education_level.name == name)
            return level.to_dict()
        except DoesNotExist:
            return None


class MessagesTypeRepository:
    """Репозиторий для работы с типами сообщений (вспомогательный)"""

    @staticmethod
    def get_all() -> List[dict]:
        """Получение всех типов сообщений"""
        types = Messages_type.select()
        return [msg_type.to_dict() for msg_type in types]

    @staticmethod
    def get_by_id(type_id: int) -> Optional[dict]:
        """Получение типа сообщения по ID"""
        try:
            msg_type = Messages_type.get(Messages_type.type == type_id)
            return msg_type.to_dict()
        except DoesNotExist:
            return None

    @staticmethod
    def get_by_name(name: str) -> Optional[dict]:
        """Получение типа сообщения по названию"""
        try:
            msg_type = Messages_type.get(Messages_type.name == name)
            return msg_type.to_dict()
        except DoesNotExist:
            return None