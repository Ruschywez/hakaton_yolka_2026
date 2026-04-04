import json
import logging
from typing import List, Dict, Any, Optional
from gigachat import GigaChat
from gigachat.models import Messages as GigaChatMessages, MessagesRole, Chat
from gigachat.exceptions import GigaChatException
from .config import GIGACHAT_CREDENTIALS, GIGACHAT_SCOPE, GIGACHAT_MODEL, SYSTEM_PROMPT_FILE

logger = logging.getLogger(__name__)

"""Зачем вы сюда смотрите T^T"""

class GigaChatClient:
    """
        Вынесение всей логики для контакта с внешним AI API в отдельынй класс
    """
    def __init__(self):
        self.credentials = GIGACHAT_CREDENTIALS # ключ авторизации
        self.scope = GIGACHAT_SCOPE # область доступа API
        self.model = GIGACHAT_MODEL # имя выбранной модели
        self.system_prompt = self._load_system_prompt() # если бы не это, то система была бы просто общением с нейронкой
        # промт подгружается из отдельного файла
        self.client = None # будущий клиент
        self._init_client()

    def _init_client(self):
        if not self.credentials or self.credentials == "your_gigachat_credentials_here":
            logger.warning("GigaChat credentials are not set or are default. Client will not be initialized.")
            return

        try:
            self.client = GigaChat(credentials=self.credentials, verify_ssl_certs=False, scope=self.scope, model=self.model)
            logger.info("GigaChat client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize GigaChat client: {e}")

    def _load_system_prompt(self) -> Dict[str, str]:
        try:
            with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {"role": data.get("role", "system"), "content": data.get("content", "")}
        except FileNotFoundError:
            logger.warning(f"System prompt file {SYSTEM_PROMPT_FILE} not found. Using default.")
            return {
                "role": "system",
                "content": "Ты — полезный карьерный ассистент."
            }
        except Exception as e:
            logger.error(f"Error loading system prompt: {e}")
            return {
                "role": "system",
                "content": "Ты — полезный карьерный ассистент."
            }

    def generate_response(self, user_message: str, history: List[Dict[str, str]] = None) -> Optional[str]:
        """
            Отправляет сообщение в GigaChat с учетом истории диалога.
            history: список словарей в формате [{"role": "user"|"assistant", "content": "text"}]
        """
        if not self.client:
            logger.error("GigaChat client is not initialized.")
            return "Извините, сервис AI временно недоступен (не настроены ключи API)."

        messages = [] # каждый раз собирается по частям
        
        # 1. Добавляем системный промпт
        if self.system_prompt.get("content"):
             messages.append(GigaChatMessages(role=MessagesRole.SYSTEM, content=self.system_prompt["content"]))

        # 2. Добавляем историю (если есть)
        if history:
            for msg in history:
                role = MessagesRole.USER if msg["role"] == "user" else MessagesRole.ASSISTANT
                messages.append(GigaChatMessages(role=role, content=msg["content"]))

        # 3. Добавляем текущее сообщение
        messages.append(GigaChatMessages(role=MessagesRole.USER, content=user_message))

        try:
            response = self.client.chat(Chat(messages=messages))
            return response.choices[0].message.content
        except GigaChatException as e:
            logger.error(f"GigaChat API error: {e}")
            return "Произошла ошибка при обращении к AI-ассистенту."
        except Exception as e:
            logger.error(f"Unexpected error when calling GigaChat: {e}")
            return "Произошла непредвиденная ошибка."

gigachat_client = GigaChatClient()
