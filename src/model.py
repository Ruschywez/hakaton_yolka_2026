# src/model.py
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status, Body
from pydantic import BaseModel

from .repositories import UserRepository, MessagesRepository, EducationLevelRepository, MessagesTypeRepository
from .gigachat_client import gigachat_client

userRepository = UserRepository()
messagesRepository = MessagesRepository()
educationLevelRepository = EducationLevelRepository()

app = FastAPI()

# ----------------- Схемы Pydantic -----------------
class UserCreate(BaseModel):
    login: str
    password: str
    last_name: str
    first_name: str
    sur_name: str
    date_birth: Optional[str] = None
    education_level: Optional[str] = None
    education_specialice: Optional[str] = None
    interests: Optional[str] = None

class UserUpdate(BaseModel):
    user_id: int
    password: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    sur_name: Optional[str] = None
    date_birth: Optional[str] = None
    education_level: Optional[str] = None
    education_specialice: Optional[str] = None
    interests: Optional[str] = None

class MessageCreate(BaseModel):
    user_id: int
    text: str
    message_type: Optional[str] = "user"

class MessageUpdate(BaseModel):
    message_id: int
    text: str

# ----------------- API Эндпоинты -----------------
@app.get("/ping")
def ping() -> bool:
    return True

@app.get("/education_levels/")
def get_education_levels():
    levels = educationLevelRepository.get_all()
    return {"levels": [lvl.get("name") for lvl in levels]}

@app.get("/user/{user_id}")
def get_user_profile(user_id: int):
    user_data = userRepository.get_by_id(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data

# --- Авторизация ---
@app.get("/authorization/")
def get_authorization(login: str, password: str):
    user_id = userRepository.get_by_login_password(login=login, password=password)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login or password")
    user_data = userRepository.get_by_id(user_id)
    return user_data

@app.post("/authorization/")
def create_authorization(user: UserCreate):
    try:
        user_id = userRepository.create(
            login=user.login,
            password=user.password,
            last_name=user.last_name,
            first_name=user.first_name,
            surname=user.sur_name,
            date_birth=user.date_birth,
            education_level=user.education_level,
            education_specialize=user.education_specialice,
            interests=user.interests
        )
        user_data = userRepository.get_by_id(user_id)
        return user_data
    except ValueError as e:
         raise HTTPException(status_code=400, detail=str(e))

@app.patch("/authorization/")
def patch_authorization(user: UserUpdate):
    update_data = {}
    if user.password is not None: update_data["password"] = user.password
    if user.last_name is not None: update_data["last_name"] = user.last_name
    if user.first_name is not None: update_data["first_name"] = user.first_name
    if user.sur_name is not None: update_data["surname"] = user.sur_name
    if user.date_birth is not None: update_data["date_birth"] = user.date_birth
    if user.education_level is not None: update_data["education_level"] = user.education_level
    if user.education_specialice is not None: update_data["education_specialize"] = user.education_specialice
    if user.interests is not None: update_data["interests"] = user.interests
    
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    
    try:
        success = userRepository.update(user_id=user.user_id, **update_data)
        if success:
            return {"message": f"User {user.user_id} updated", "updated_fields": update_data}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/authorization/{user_id}")
def delete_authorization(user_id: int):
    success = userRepository.delete(user_id)
    if success:
        return {"message": f"User {user_id} successfully deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


# --- Сообщения ---
@app.get("/messages/")
def get_messages(user_id: int):
    messages = messagesRepository.get_by_user(user_id)
    if not messages:
        return {"messages": []}
    
    formatted_messages = [
        {"message_id": msg[0], "text": msg[1], "type": msg[2], "date_time": msg[3].isoformat() if isinstance(msg[3], datetime) else msg[3]}
        for msg in messages
    ]
    return {"messages": formatted_messages}

@app.post("/messages/")
def create_message(msg: MessageCreate):
    # Убеждаемся, что пользователь существует
    user_data = userRepository.get_by_id(msg.user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. Сохраняем сообщение пользователя
    user_msg_type = "user"
    success = messagesRepository.create(user_id=msg.user_id, text=msg.text, message_type=user_msg_type)
    if not success:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save user message")

    # 2. Получаем историю
    history = messagesRepository.get_history_for_ai(msg.user_id)
    # Удаляем последнее сообщение пользователя из истории, так как gigachat_client получает его отдельно 1 параметром
    if history and history[-1]["role"] == "user":
        history = history[:-1]

    # Если мы не инициализировали системный промпт специфично для пользователя, 
    # мы можем добавить его контекст прямо в сообщение
    user_context = f"\nКонтекст пользователя: Имя {user_data.get('first_name', '')}, Образование: {user_data.get('education_level', '')}, Интересы: {user_data.get('interest', '')}"
    ai_input = msg.text + user_context
    
    # 3. Отправляем в GigaChat
    # history = [] если хотите, но gigachat_client ожидает формат dict
    assistant_text = gigachat_client.generate_response(ai_input, history=history)

    # 4. Сохраняем ответ системы
    assistant_msg_type = "assistant"
    messagesRepository.create(user_id=msg.user_id, text=assistant_text, message_type=assistant_msg_type)

    # Получаем последнее (созданное) сообщение ассистента чтобы вернуть его с ID и датой
    all_msgs = messagesRepository.get_by_user(msg.user_id)
    if all_msgs and len(all_msgs) > 0:
        latest = all_msgs[0] # desc order
        return {
            "message_id": latest[0],
            "text": latest[1],
            "type": latest[2],
            "date_time": latest[3].isoformat() if isinstance(latest[3], datetime) else latest[3]
        }
    else:
        return {"message": "Message created, but could not load it back."}

@app.patch("/messages/")
def patch_message(msg: MessageUpdate):
    success = messagesRepository.update(message_id=msg.message_id, text=msg.text)
    if success:
        return {"message": f"Message {msg.message_id} updated"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

@app.delete("/messages/{message_id}")
def delete_message(message_id: int):
    success = messagesRepository.delete(message_id)
    if success:
        return {"message": f"Message {message_id} successfully deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")