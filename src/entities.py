from peewee import AutoField, CharField, Check, DateTimeField, ForeignKeyField, Model
from .db_connect import create_db_connect

class BaseModel(Model): # Класс для подключения!
    class Meta:
        database = create_db_connect()

class Education_level(BaseModel):
    level = AutoField(primary_key=True, column_name="level_id")
    name = CharField(max_length=100, unique=True)
    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "name": self.name,
        }
class User(BaseModel):
    user = AutoField(primary_key=True, column_name="user_id")
    login = CharField(max_length=100, unique=True)
    password = CharField(max_length=100)

    last_name = CharField(max_length=100, column_name="lastname")
    first_name = CharField(max_length=100, column_name="firstname")
    surname = CharField(max_length=100)
    date_birth = CharField(max_length=20, null=True)

    education_level = ForeignKeyField(Education_level, backref='education', on_delete='CASCADE', on_update='CASCADE', column_name="education_level_fk", null=True)
    education_specialize = CharField(max_length=512, null=True)
    interests = CharField(max_length=1024, null=True)

    def to_dict(self) -> dict:
        return {
            "user": self.user,
            "login": self.login,
            "password": self.password,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "surname": self.surname,
            "date_birth": self.date_birth,
            "education_level": self.education_level.name if self.education_level else None,
            "education_specialize": self.education_specialize,
            "interests": self.interests
        }
class Messages_type(BaseModel):
    type = AutoField(primary_key=True, column_name="type_id")
    name = CharField(max_length=100, unique=True)
    def to_dict(self) -> dict:
        return {
            "type_id": self.type,
            "name": self.name,
        }
class Messages(BaseModel):
    message = AutoField(primary_key=True, column_name="message_id")
    user = ForeignKeyField(User, backref='user_messages', on_delete='CASCADE', on_update='CASCADE', column_name="user_fk")
    type = ForeignKeyField(Messages_type, backref='type_messages', on_delete='CASCADE', on_update='CASCADE', column_name="type_fk")
    text = CharField(max_length=4000)
    date_time = DateTimeField()
    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "user": self.user.user if hasattr(self.user, 'user') else self.user,
            "type": self.type.type if hasattr(self.type, 'type') else self.type,
            "text": self.text,
            "date_time": self.date_time
        }
    