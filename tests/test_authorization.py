import pytest
import allure
import api
import HTTP_status
import error_responses
from settings import valid_password, valid_email, test_user1, test_user2, non_existent_email, non_existent_password


auth = api.AuthToken()
user = api.Users()


class TestAuthorisationBasic:
    # Базовый позитивный тест на создание токена при аутентификации зарегистрированного пользователя
    @pytest.mark.high
    @pytest.mark.smoke
    @allure.story('Authorization')
    @allure.title('Аутентификация зарегистрированного пользователя')
    def test_authorisation_positive(self):
        # Step 1. Create token for registered user
        with allure.step('Create token for user with valid data'):
            status, response = auth.create_token(email=test_user1["email"], password=test_user1["password"])
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code is 200'):
            assert status == HTTP_status.HTTP_200_OK
        with allure.step('Check refresh and access tokens in response'):
            assert response['refresh'] is not None
            assert response['access'] is not None
            access_token = response['access']

        #Step 2. Get user's info
        with allure.step('Get user info with valid access token'):
            status, response = user.get_user(token=access_token)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
            assert status == HTTP_status.HTTP_200_OK
            assert response['role'] == test_user1["role"]
            assert response['id'] == test_user1["id"]
            assert response['email'] == test_user1["email"]


# Негативные тесты


class TestAuthorizationModule:
    # Тесты на отсутствие обязательных полей
    @pytest.mark.high
    @pytest.mark.parametrize(
        ("data", 'field'),
        [
            ({"password": valid_password}, 'email'),
            ({"email": valid_email}, 'password')
        ],
        ids=['without email', 'without password']
    )
    @allure.title('Невозможность аутентификации без обязательных полей')
    def test_create_token_without_required_fields(self, data, field):
        with allure.step('Send request for create tokens'):
            status, response = auth.create_token(email=None, password=None, data=data)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code'):
            assert status != HTTP_status.HTTP_200_OK
            assert status == HTTP_status.HTTP_400_BAD_REQUEST
        with allure.step('Check response'):
            assert error_responses.ERROR_REQUIRED_FIELD in response[field][0]

    # Тесты на запрос с невалидными данными (несоответствие email, password пользователя)
    @pytest.mark.high
    @pytest.mark.parametrize(
        ("data", 'field'),
        [
            ({"email": test_user2["email"], "password": test_user1["password"]}, 'email'),
            ({"email": test_user1["email"], "password": test_user2["password"]}, 'password')
        ],
        ids=['invalid email', 'invalid password']
    )
    @allure.title('Невозможность аутентификации при несовпадении email и пароля')
    def test_create_token_with_invalid_data(self, data, field):
        with allure.step('Send request for create tokens'):
            status, response = auth.create_token(email=None, password=None, data=data)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code'):
            assert status != HTTP_status.HTTP_200_OK
            assert status == HTTP_status.HTTP_401_UNAUTHORIZED
        with allure.step('Check response'):
            assert response['detail'] == error_responses.ERROR_AUTHORISATION

    # Тест на запрос с несуществующими в БД данными
    @pytest.mark.high
    @allure.title('Невозможность аутентификации незарегистрированного в БД пользователя')
    def test_create_token_with_non_existent_data(self):
        with allure.step('Send request for create tokens'):
            status, response = auth.create_token(email=non_existent_email, password=non_existent_password)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code'):
            assert status != HTTP_status.HTTP_200_OK
            assert status == HTTP_status.HTTP_401_UNAUTHORIZED
        with allure.step('Check response'):
            assert response['detail'] == error_responses.ERROR_AUTHORISATION


    # Тесты на запрос со значением Null в Not null полях
    @pytest.mark.high
    @pytest.mark.parametrize(
        ("data", 'field'),
        [
            ({"email": None, "password": test_user1["password"]}, 'email'),
            ({"email": test_user1["email"], "password": None}, 'password')
        ],
        ids=['Null email', 'Null password']
    )
    @allure.title('Невозможность аутентификации с null данными')
    def test_create_token_with_null_data(self, data, field):
        with allure.step('Send request for create tokens'):
            status, response = auth.create_token(email=None, password=None, data=data)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code'):
            assert status != HTTP_status.HTTP_200_OK
            assert status == HTTP_status.HTTP_400_BAD_REQUEST
        with allure.step('Check response'):
            assert response[field][0] == error_responses.ERROR_NOT_NULL_FIELD


    # Тесты на запрос с незаполненным значением в Not null полях
    @pytest.mark.high
    @pytest.mark.parametrize(
        ("data", 'field'),
        [
            ({"email": "", "password": test_user1["password"]}, 'email'),
            ({"email": test_user1["email"], "password": ""}, 'password')
        ],
        ids=['empty string email', 'empty string password']
    )
    @allure.title('Невозможность аутентификации с пустыми данными')
    def test_create_token_with_empty_data(self, data, field):
        with allure.step('Send request for create tokens'):
            status, response = auth.create_token(email=None, password=None, data=data)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code'):
            assert status != HTTP_status.HTTP_200_OK
            assert status == HTTP_status.HTTP_400_BAD_REQUEST
        with allure.step('Check response'):
            assert response[field][0] == error_responses.ERROR_EMPTY_FIELD
