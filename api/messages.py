"""API сообщений."""

import random
import time
from datetime import datetime
from config import MOCK_MODE
from api.client import client

MOCK_MESSAGES = [
    {
        'message_id': 1,
        'text': 'Привет! Чем ты можешь мне помочь?',
        'type': 'user',
        'date_time': '2026-04-03 10:00:00'
    },
    {
        'message_id': 2,
        'text': (
            'Привет! Я ВолодяGPT — твой персональный карьерный ассистент!\n\n'
            'Я могу помочь тебе:\n'
            '  - Определиться с будущей профессией\n'
            '  - Найти подходящие вакансии\n'
            '  - Составить план развития навыков\n'
            '  - Построить карьерный путь\n\n'
            'Расскажи о себе — чем ты интересуешься?'
        ),
        'type': 'assistant',
        'date_time': '2026-04-03 10:00:05'
    }
]

MOCK_AI_RESPONSES = [
    (
        "Интересный вопрос! Исходя из твоих интересов, я бы порекомендовал:\n\n"
        "  - Data Science — анализ данных и машинное обучение\n"
        "  - Web-разработка — современные веб-приложения\n"
        "  - DevOps — автоматизация инфраструктуры\n\n"
        "Какое из них тебе ближе?"
    ),
    (
        "Отлично! Вот что рекомендую для старта:\n\n"
        "  1. Изучи основы Python\n"
        "  2. Пройди онлайн-курс по специальности\n"
        "  3. Создай портфолио из 2-3 проектов\n"
        "  4. Начни искать стажировки\n\n"
        "Хочешь, расскажу подробнее?"
    ),
    (
        "По твоему профилю я подобрал вакансии:\n\n"
        "  - Junior Python Developer — МТС, Москва (от 60 000 руб.)\n"
        "  - Стажёр Data Analyst — Яндекс, удалённо\n"
        "  - Помощник ML-инженера — Сбер, СПб\n\n"
        "Хочешь узнать подробнее?"
    ),
    (
        "Давай составим план развития на 6 месяцев:\n\n"
        "  Месяц 1-2: Основы программирования\n"
        "  Месяц 3-4: Специализированные курсы\n"
        "  Месяц 5: Pet-проект для портфолио\n"
        "  Месяц 6: Резюме и поиск стажировки\n\n"
        "Начнём?"
    ),
    (
        "На рынке труда сейчас востребованы:\n\n"
        "  - Аналитики данных — рост спроса 45%\n"
        "  - ML/AI инженеры — зарплата от 150 000 руб.\n"
        "  - Cloud-инженеры — нехватка специалистов\n"
        "  - Кибербезопасность — критически важно\n\n"
        "Рекомендую обратить внимание на AI/ML."
    ),
    (
        "Для старта карьеры в IT важно:\n\n"
        "  - Крепкая база в языке программирования\n"
        "  - Основы алгоритмов и структур данных\n"
        "  - Умение работать с Git\n"
        "  - Минимум один завершённый проект\n\n"
        "Что из этого у тебя уже есть?"
    ),
    (
        "Карьерный путь в IT:\n\n"
        "  Стажёр -> Junior -> Middle -> Senior -> Lead\n\n"
        "На каждом этапе важны и технические навыки, "
        "и soft skills: коммуникация, работа в команде.\n\n"
        "На каком этапе ты сейчас?"
    ),
]

_mock_counter = 2


def get_messages(user_id):
    """GET /messages/ — получить сообщения."""
    if MOCK_MODE:
        return MOCK_MESSAGES.copy()
    response = client.get('messages/', params={'user_id': user_id})
    if isinstance(response, dict) and 'messages' in response:
        return response.get('messages', [])
    return response if isinstance(response, list) else []


def send_message(user_id, text):
    """POST /messages/ — отправить сообщение."""
    global _mock_counter
    if MOCK_MODE:
        _mock_counter += 1
        user_msg = {
            'message_id': _mock_counter,
            'text': text, 'type': 'user',
            'date_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        MOCK_MESSAGES.append(user_msg)
        time.sleep(1.5)
        _mock_counter += 1
        ai_msg = {
            'message_id': _mock_counter,
            'text': random.choice(MOCK_AI_RESPONSES),
            'type': 'assistant',
            'date_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        MOCK_MESSAGES.append(ai_msg)
        return ai_msg
    return client.post('messages/', data={'user_id': user_id, 'text': text})


def edit_message(message_id, text):
    """PATCH /messages/ — редактировать сообщение."""
    if MOCK_MODE:
        for msg in MOCK_MESSAGES:
            if msg['message_id'] == message_id:
                msg['text'] = text
                break
        return True
    return client.patch('messages/', data={'message_id': message_id, 'text': text})


def delete_message(message_id):
    """DELETE /messages/ — удалить сообщение."""
    if MOCK_MODE:
        for i, msg in enumerate(MOCK_MESSAGES):
            if msg['message_id'] == message_id:
                MOCK_MESSAGES.pop(i)
                break
        return True
    return client.delete(f'messages/{message_id}')
