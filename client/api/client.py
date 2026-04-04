"""HTTP-клиент для взаимодействия с API."""

import requests
from config import API_BASE_URL, MOCK_MODE


class APIError(Exception):
    """Ошибка API-запроса."""
    pass


class APIClient:
    """Обёртка HTTP-клиента для API."""

    def __init__(self):
        self.base_url = API_BASE_URL.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _url(self, endpoint):
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def get(self, endpoint, params=None):
        if MOCK_MODE:
            return None
        try:
            resp = self.session.get(self._url(endpoint), params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"GET {endpoint}: {e}")

    def post(self, endpoint, data=None):
        if MOCK_MODE:
            return None
        try:
            resp = self.session.post(self._url(endpoint), json=data, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"POST {endpoint}: {e}")

    def patch(self, endpoint, data=None):
        if MOCK_MODE:
            return None
        try:
            resp = self.session.patch(self._url(endpoint), json=data, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"PATCH {endpoint}: {e}")

    def delete(self, endpoint, params=None):
        if MOCK_MODE:
            return None
        try:
            resp = self.session.delete(self._url(endpoint), params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"DELETE {endpoint}: {e}")


client = APIClient()
