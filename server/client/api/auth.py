"""API авторизации."""

from config import MOCK_MODE
from api.client import client

MOCK_USER_DATA = {
    'user_id': 1,
    'login': 'demo',
    'first_name': 'Егор',
    'last_name': 'Васильев',
    'sur_name': 'Александрович',
    'date_birth': '2005-06-15',
    'education_level': 'Студент вуза',
    'education_specialice': 'Информационные технологии',
    'interest': 'Программирование, Искусственный интеллект, Data Science'
}


def login(login_str, password):
    """GET /authorization/ — вход."""
    if MOCK_MODE:
        return {**MOCK_USER_DATA, 'login': login_str}
    return client.get('authorization/', params={'login': login_str, 'password': password})


def register(login_str, password, last_name, first_name, sur_name, date_birth):
    """POST /authorization/ — регистрация."""
    if MOCK_MODE:
        return {
            'user_id': 1, 'login': login_str,
            'first_name': first_name, 'last_name': last_name,
            'sur_name': sur_name, 'date_birth': date_birth,
            'education_level': '', 'education_specialice': '', 'interest': ''
        }
    return client.post('authorization/', data={
        'login': login_str, 'password': password,
        'last_name': last_name, 'first_name': first_name,
        'sur_name': sur_name, 'date_birth': date_birth
    })


def update_profile(**kwargs):
    """PATCH /authorization/ — обновление профиля."""
    data = {k: v for k, v in kwargs.items() if v}
    if MOCK_MODE:
        MOCK_USER_DATA.update(data)
        return True
    return client.patch('authorization/', data=data)


def delete_account(user_id):
    """DELETE /authorization/ — удаление аккаунта."""
    if MOCK_MODE:
        return True
    return client.delete(f'authorization/{user_id}')
