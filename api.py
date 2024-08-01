from typing import Tuple, Union, Dict, Any
import requests
import json
import routers
import HTTP_params


class CustInsights:
    """Общая библиотека к приложению Cust Insights"""
    def __init__(self):
        self.base_url = routers.BASE_URL

    def _check_headers(self, headers: dict, default: dict):
        """Общий метод для выбора заголовков"""
        if headers is None:
            return default
        return headers

    def union_headers(self, header1: dict, header2: dict, ):
        union_header = {**header1, **header2}
        return union_header

    def _check_url(self, url, default):
        """Общий метод для выбора url"""
        if url is None:
            return default
        return url

    def _check_data(self, data, default):
        """Общий метод для выбора данных"""
        if data is None:
            return default
        return data

    def _make_request(
            self, method: str, url: str, endpoint: str, headers: Dict = None, params: Dict = None, data: Dict = None
    ) -> Tuple[int, Union[Tuple[Dict[str, Any]], str]]:
        """Общий метод для выполнения запросов"""
        res = requests.request(method, url + endpoint, headers=headers, params=params, json=data)
        try:
            result = res.json(),
            response = result[0]
        except json.decoder.JSONDecodeError:
            response = res.text
        return res.status_code, response


class AuthToken(CustInsights):
    """Класс для работы с токенами"""
    def create_token(
            self, email: str, password: str, url=None, headers=None, data=None
    ) -> Tuple[int, Union[Dict[str, Any], str]]:
        """Метод создания токена при авторизации пользователя"""
        headers = self._check_headers(headers, default=HTTP_params.CONTENT_TYPE_JSON)
        url = self._check_url(url, default=self.base_url)
        data = self._check_data(data, default={
            'email': email,
            'password': password
        })
        request = self._make_request(method='post', url=url, endpoint=routers.TOKEN_CREATE, headers=headers, data=data)
        return request

    def blacklist_token(
            self, token: str, refresh_token: str, url=None, headers=None, data=None
    ) -> Tuple[int, Union[Dict[str, Any], str]]:
        """Метод перемещения токена пользователя в blacklist после log out"""
        headers = self._check_headers(headers, default=self.union_headers(
            HTTP_params.AUTHORIZATION_TOKEN(token), HTTP_params.CONTENT_TYPE_JSON
        ))
        url = self._check_url(url, default=self.base_url)
        data = self._check_data(data, default={
            'refresh': refresh_token
        })
        request = self._make_request(
            method='post', url=url, endpoint=routers.TOKEN_BLACKLIST, headers=headers, data=data
        )
        return request


class Users(CustInsights):
    """Класс для работы с пользователями"""
    def add_user(
            self, email: str, password: str, role: str, url=None, headers=None, data=None
    ) -> Tuple[int, Union[Dict[str, Any], str]]:
        """Метод создания нового пользователя с выбранной ролью"""
        headers = self._check_headers(headers, default=HTTP_params.CONTENT_TYPE_JSON)
        url = self._check_url(url, default=self.base_url)
        data = self._check_data(data, default={
            'email': email,
            'password': password,
            'role': role
        })
        request = self._make_request(method='post', url=url, endpoint=routers.USERS, headers=headers, data=data)
        return request

    def get_user(self, token=None, url=None, headers=None) -> Tuple[int, Union[Dict[str, Any], str]]:
        """Метод получения информации о пользователе после авторизации"""
        headers = self._check_headers(headers, default=HTTP_params.AUTHORIZATION_TOKEN(token))
        url = self._check_url(url, default=self.base_url)
        request = self._make_request(method='get', url=url, endpoint=routers.USER, headers=headers, data=None)
        return request

    def delete_user(
            self, password: str, token: str, url=None, headers=None, data=None
    ) -> Tuple[int, Union[Dict[str, Any], str]]:
        """Метод удаления пользователя"""
        headers = self._check_headers(headers, default=self.union_headers(
            HTTP_params.AUTHORIZATION_TOKEN(token), HTTP_params.CONTENT_TYPE_JSON
        ))
        url = self._check_url(url, default=self.base_url)
        data = self._check_data(data, default={
            'current_password': password
        })
        request = self._make_request(method='delete', url=url, endpoint=routers.USER, headers=headers, data=data)
        return request


class RespondentProfile(CustInsights):
    """Класс для работы с профилем респондента"""
    def create_profile(self, token=None, url=None, headers=None, data=None) -> Tuple[int, Union[Dict[str, Any], str]]:
        """Метод создания профиля респондента"""
        headers = self._check_headers(headers, default=self.union_headers(
            HTTP_params.AUTHORIZATION_TOKEN(token), HTTP_params.CONTENT_TYPE_JSON
        ))
        url = self._check_url(url, default=self.base_url)
        data = self._check_data(data, default=None)
        request = self._make_request(method='post', url=url, endpoint=routers.RESPONDENTS, headers=headers, data=data)
        return request

    def get_profile(self, token=None, url=None, headers=None) -> Tuple[int, Union[Dict[str, Any], str]]:
        """Метод получения профиля респондента"""
        headers = self._check_headers(headers, default=HTTP_params.AUTHORIZATION_TOKEN(token))
        url = self._check_url(url, default=self.base_url)
        request = self._make_request(method='get', url=url, endpoint=routers.RESPONDENT, headers=headers)
        return request

    def delete_profile(self, token=None, url=None, headers=None, data=None) -> Tuple[int, Union[Dict[str, Any], str]]:
        """Метод создания профиля респондента"""
        headers = self._check_headers(headers, default=self.union_headers(
            HTTP_params.AUTHORIZATION_TOKEN(token), HTTP_params.CONTENT_TYPE_JSON
        ))
        url = self._check_url(url, default=self.base_url)
        data = self._check_data(data, default=None)
        request = self._make_request(method='delete', url=url, endpoint=routers.RESPONDENT, headers=headers, data=data)
        return request
