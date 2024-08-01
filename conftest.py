import pytest
from datetime import datetime
import api


@pytest.fixture(autouse=True)
def time_delta():
    start_time = datetime.now()
    yield
    end_time = datetime.now()
    test_time = (end_time - start_time).total_seconds()
    print(f"\nTest time is: {test_time}")
    # if test_time <= 1:
    #     print('Test time less 1 sec')
    # else:
    #     print('Test failed\n')


@pytest.fixture
def user():
    return api.Users()


@pytest.fixture
def auth():
    return api.AuthToken()


@pytest.fixture
def respondent():
    return api.RespondentProfile()


@pytest.fixture(scope='function')
def get_auth_token(auth):
    def _get_token(email: str, password: str):
        status, response = auth.create_token(email, password)
        if status == 200:
            auth_token = response['access']
            print('\nТокен получен')
            return auth_token
        else:
            print(f'\nОшибка получения токена: status: {status}; result: {response}')
            return None
    return _get_token


@pytest.fixture(scope='function')
def delete_user(user):
    def _delete(password: str, token: str):
        status, response = user.delete_user(password, token)
        if status == 204:
            print('\nПользователь удален')
            return True
        else:
            print(f'\nОшибка удаления пользователя: status: {status}; result: {response}')
            return False
    return _delete


@pytest.fixture(scope='function')
def delete_respondent_profile(respondent):
    def _delete(token: str):
        status, response = respondent.delete_profile(token)
        if status == 204:
            print('\nПрофиль удален')
            return True
        else:
            print(f'\nОшибка удаления профиля: status: {status}; result: {response}')
            return False
    return _delete
