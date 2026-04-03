# main.py
from .repositories import UserRepository, MessagesRepository, EducationLevelRepository, MessagesTypeRepository
from .entities import User, Messages
from fastapi import FastAPI, Query, HTTPException, status
from datetime import datetime
from typing import Optional, List, Tuple

userRepository = UserRepository()
messagesRepository = MessagesRepository()

app = FastAPI()

@app.get("/ping") # проверка подключения
def ping() -> bool:
    return True


"""Authorization - авторизация"""
@app.get("/authorization/")
def get_authorization(
    login: str = Query(..., min_length=1, max_length=100),
    password: str = Query(..., min_length=1, max_length=100)
):
    user_id = userRepository.get_by_login_password(login=login, password=password)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login or password")
    return {"user_id": user_id}

@app.post("/authorization/")
def create_authorization(
    login: str = Query(..., min_length=1, max_length=100),
    password: str = Query(..., min_length=1, max_length=100),
    last_name: str = Query(..., min_length=1, max_length=100),
    first_name: str = Query(..., min_length=1, max_length=100),
    sur_name: str = Query(..., min_length=1, max_length=100),
    date_birth: Optional[str] = Query(None),  # строка с датой, можно потом парсить
    education_level: Optional[int] = Query(None, ge=0),
    education_specialice: Optional[str] = Query(None, max_length=512),
    interests: Optional[str] = Query(None, max_length=1024)
):
    user_id = userRepository.create(
        login=login,
        password=password,
        last_name=last_name,
        first_name=first_name,
        surname=sur_name,
        date_birth=date_birth,
        education_level=education_level,
        education_specialize=education_specialice,
        interests=interests
    )
    return {"user_id": user_id}

@app.patch("/authorization/")
def patch_authorization(
    user_id: int = Query(..., ge=0),
    password: Optional[str] = Query(None, min_length=1, max_length=100),
    last_name: Optional[str] = Query(None, min_length=1, max_length=100),
    first_name: Optional[str] = Query(None, min_length=1, max_length=100),
    sur_name: Optional[str] = Query(None, min_length=1, max_length=100),
    date_birth: Optional[str] = Query(None),
    education_level: Optional[int] = Query(None, ge=0),
    education_specialice: Optional[str] = Query(None, max_length=512),
    interests: Optional[str] = Query(None, max_length=1024)
):
    update_data = {}
    if password is not None:
        update_data["password"] = password
    if last_name is not None:
        update_data["last_name"] = last_name
    if first_name is not None:
        update_data["first_name"] = first_name
    if sur_name is not None:
        update_data["surname"] = sur_name
    if date_birth is not None:
        update_data["date_birth"] = date_birth
    if education_level is not None:
        update_data["education_level"] = education_level
    if education_specialice is not None:
        update_data["education_specialize"] = education_specialice
    if interests is not None:
        update_data["interests"] = interests
    
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    
    success = userRepository.update(user_id=user_id, **update_data)
    if success:
        return {"message": f"User {user_id} updated", "updated_fields": update_data}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@app.delete("/authorization/{user_id}")
def delete_authorization(user_id: int):
    success = userRepository.delete(user_id)
    if success:
        return {"message": f"User {user_id} successfully deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


"""Messages - сообщения"""
@app.get("/messages/")
def get_messages(user_id: int = Query(..., ge=0)):
    messages = messagesRepository.get_by_user(user_id)
    if not messages:
        return {"messages": []}
    
    # Форматируем результат как в ТЗ: [(message_id, text, type, date_time)]
    formatted_messages = [
        {"message_id": msg[0], "text": msg[1], "type": msg[2], "date_time": msg[3].isoformat() if isinstance(msg[3], datetime) else msg[3]}
        for msg in messages
    ]
    return {"messages": formatted_messages}

@app.post("/messages/")
def create_message(
    user_id: int = Query(..., ge=0),
    text: str = Query(..., min_length=1, max_length=4000),
    message_type: Optional[int] = Query(1, ge=0)  # тип сообщения по умолчанию 1
):
    success = messagesRepository.create(user_id=user_id, text=text, message_type=message_type)
    if success:
        return {"message": "Message created successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@app.patch("/messages/")
def patch_message(
    message_id: int = Query(..., ge=0),
    text: str = Query(..., min_length=1, max_length=4000)
):
    success = messagesRepository.update(message_id=message_id, text=text)
    if success:
        return {"message": f"Message {message_id} updated"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

@app.delete("/messages/{message_id}")
def delete_message(message_id: int):
    success = messagesRepository.delete(message_id)
    if success:
        return {"message": f"Message {message_id} successfully deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")