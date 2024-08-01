import pytest
import allure
from faker import Faker
import api
import HTTP_status
import error_responses
from settings import valid_password, valid_email, test_user1, role_resp, role_researcher, random_string, random_digits,\
    random_special, random_cyrillics


auth = api.AuthToken()
user = api.Users()
fake = Faker(['ru_RU'])


class TestRegistrationBasic:
    # Базовый позитивный тест на создание пользователя при регистрации (без подтверждения почты)
    @pytest.mark.high
    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "role",
        [
            role_resp,
            role_researcher
        ],
        ids=['add respondent', 'add researcher']
    )
    @allure.story('Registration')
    @allure.title('Регистрация пользователя с валидными данными и ролью')
    def test_add_user(self, get_auth_token, delete_user, role, email=valid_email, password=valid_password):
        # Step 1. Create user with valid data
        with allure.step('Create user with valid data'):
            status, response = user.add_user(email, password, role=role)
            print(f'\nОтвет сервера: status: {status}; response: {response}')
        with allure.step('Check status code is 201'):
            assert status == HTTP_status.HTTP_201_CREATED
        with allure.step("Check user's data in response"):
            assert 'id' in response
            user_id = response['id']
            assert response['role'] == role
            assert response['email'] == email

        # Step 2. Check user is saved in DB
        with allure.step('Get user from DB'):
            access_token = get_auth_token(email=email, password=password)
            status, response = user.get_user(token=access_token)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
            assert status == HTTP_status.HTTP_200_OK
            assert response['role'] == role
            assert response['id'] == user_id
            assert response['email'] == email

        # Step 3. Postconditions: Delete user in DB
        with allure.step('Postconditions: Delete user in DB'):
            delete_user(password=password, token=access_token)

    @pytest.mark.high
    @pytest.mark.smoke
    @allure.story('Registration')
    @allure.title('Невозможность добавить пользователя с уже зарегистрированным email')
    def test_add_registered_user(
            self, email=test_user1['email'], password=test_user1['password'], role=test_user1['role']
    ):
        with allure.step('Send request for add user with existent email'):
            status, response = user.add_user(email, password, role)
        print(f'\nОтвет сервера: status: {status}; response: {response}')
        with allure.step('Check status code'):
            assert status != HTTP_status.HTTP_201_CREATED
            assert status == HTTP_status.HTTP_400_BAD_REQUEST
        with allure.step('Check response'):
            assert 'id' not in response
            assert error_responses.ERROR_EXIST_USER in response["email"]


class TestEmailValidation:
    @pytest.mark.high
    @pytest.mark.parametrize(
        "email",
        [
            f'{random_string(5).lower()}@{fake.domain_name()}',
            f'{random_string(5).upper()}@{fake.domain_name()}',
            f'{random_string(5).lower()}{random_digits(1)}@{fake.domain_name()}',
            f'{random_string(5).lower()}@{random_digits(1)}{fake.domain_name()}',
            f'{random_string(5).lower()}-{random_string(3).lower()}@{fake.domain_name()}',
            f'{random_string(5).lower()}@{random_string(3).lower()}-{random_string(3).lower()}.com',
            f'{random_string(5).lower()}_{random_string(3).lower()}@{fake.domain_name()}',
            f'{random_string(5).lower()}.{random_string(3).lower()}@{fake.domain_name()}',
            f'{random_string(5).lower()}@{random_string(3).lower()}.{random_string(3).lower()}.com',
            f'{random_string(5).lower()}@{fake.ipv4()}',
            f'_{random_string(5).lower()}@{fake.domain_name()}',
            f'{random_string(5).lower()}_@{fake.domain_name()}',
            f' {random_string(5).lower()}@{fake.domain_name()}',
            f'{random_string(5).lower()}@{fake.domain_name()} '
        ],
        ids=[
            'Email lower case',
            'Email upper case',
            'Email with numbers in address',
            'Email with numbers in domain',
            'Email with hyphen in address',
            'Email with hyphen in domain',
            'Email with underscore in address',
            'Email with dot in address',
            'Email with dots in domain',
            'IP format in domain',
            'Leading _ in address',
            'Trailing _ in address',
            'Leading whitespace',
            'Trailing whitespace'
        ]
    )
    @allure.title('Проверка регистрации с валидным email')
    def test_add_user_with_valid_email(self, get_auth_token, delete_user, email):
        with allure.step('Send request for add user with valid email'):
            status, response = user.add_user(email=email, password=valid_password, role=role_resp)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code is 201'):
            assert status == HTTP_status.HTTP_201_CREATED
            print('User added')
        with allure.step('Check response'):
            assert 'id' in response
        with allure.step('Postconditions: Delete user'):
            access_token = get_auth_token(email=email, password=valid_password)
            delete_user(password=valid_password, token=access_token)

    @pytest.mark.high
    @pytest.mark.parametrize(
        "email",
        [
            f'{random_string(7).lower()}',
            f'{random_string(5).lower()}.{fake.domain_name()}',
            f'{fake.domain_name()}',
            f'{fake.name()} <{random_string(5).lower()}@{fake.domain_name()}>',
            f'{random_string(5).lower()}@{fake.domain_name()} ({fake.name()})',
            f'{random_string(5).lower()}@{random_string(5).lower()}@{fake.domain_name()}',
            f'.{random_string(5).lower()}@{fake.domain_name()}',
            f'{random_string(5).lower()}.@{fake.domain_name()}',
            f'{random_string(5).lower()}..{random_string(5).lower()}@{fake.domain_name()}',
            # 'あいうえお@domain.com',
            f'{random_string(5).lower()}@-{fake.domain_name()}',
            f'{random_string(5).lower()}@.{fake.domain_name()}',
            f'{random_string(5).lower()}@{random_string(5).lower()}..com',
            f'{random_string(5).lower()}@{random_string(5).lower()}com',
            'OXLYsrank6l8eWBhtsZUnmxsaoGfsYZpear8OTRtpUG0Tlrt50N5ZNwYV12BMCZf.OXLYsrank6l8eWBhtsZUnmxsaoGfsYZpear8OTRtpUG0Tlrt50N5ZNwYV12BMhgd.OXLYsrank6l8eWBhtsZUnmxsaoGfsYZpear8OTRtpUG0Tlrt50N5ZNwYV12BMhgd-OXLYsrank6l8eWBhGfsYZpeaN5ZNw@OXLYsraYZpear8OTRwYV12BMhgd.OXLYsrank6l8eWBhtsZUnmxsaoGfsYZpear8OTRtpUG0Tlrt50N5ZNwYV12BMhgd.com',
            f'{random_string(3).lower()} {random_string(3).lower()}@{fake.domain_name()}',
            f'{random_string(5).lower()}@{random_string(3).lower()} {random_string(2).lower()}.com',
            f'{random_string(5).lower()}@.com',
            f'{random_string(5).lower()}@{random_string(3).lower()}.{random_string(64).lower()}',
            f'{random_string(5).lower()}@{random_string(2).lower()}_{random_string(4).lower()}.com',
            f'{random_cyrillics(5).lower()}@{fake.domain_name()}'
        ],
        ids=[
            'No @ and domain',
            'Missing @',
            'Missing address',
            'Copy/paste from address book with name',
            'Superfluous text',
            'Two @',
            'Leading dot in address',
            'Trailing dot in address',
            'Multiple dots',
            # 'Unicode chars in address',
            'Leading dash in domain',
            'Leading dot in domain',
            'Multiple dots in the domain',
            'Email without dots in domain',
            'Too long email (>254 symbols)',
            'Email with whitespace in address',
            'Email with whitespace in domain',
            'Email without domain',
            'Incorrect domain (more 63 symbols after .)',
            'Email with _ in domain',
            'Email with cyrillic in address'
        ]
    )
    @allure.title('Проверка аутентификации с невалидным email')
    def test_add_user_with_invalid_email(self, get_auth_token, delete_user, email):
        with allure.step('Send request for add user with invalid email'):
            status, response = user.add_user(email=email, password=valid_password, role=role_resp)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code'):
            if status != HTTP_status.HTTP_201_CREATED:
                assert status == HTTP_status.HTTP_400_BAD_REQUEST
                with allure.step('Check response'):
                    assert error_responses.ERROR_INVALID_EMAIL in str(response)
            else:
                print('User added')
                access_token = get_auth_token(email=email, password=valid_password)
                delete_user(password=valid_password, token=access_token)

class TestPasswordValidation:
    @pytest.mark.high
    @pytest.mark.parametrize(
        "password",
        [
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}!',
            f'{random_string(1).upper() + random_string(97).lower() + random_digits(1)}!',
            f' {random_string(1).upper() + random_string(5).lower() + random_digits(1)}!',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}! '
        ],
        ids=[
            '8 symbols latin upper and lower, number, special char',
            '100 symbols latin upper and lower, number, special char',
            'Leading whitespace',
            'Trailing whitespace'
        ]
    )
    @allure.title('Проверка аутентификации с валидным password')
    def test_add_user_with_valid_password(self, get_auth_token, delete_user, password):
        with allure.step('Send request for add user with valid password'):
            status, response = user.add_user(email=valid_email, password=password, role=role_resp)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code is 201'):
            assert status == HTTP_status.HTTP_201_CREATED
            print('User added')
        with allure.step('Check response'):
            assert 'id' in response
        with allure.step('Postconditions: Delete user'):
            access_token = get_auth_token(email=valid_email, password=password)
            delete_user(password=password, token=access_token)

    @pytest.mark.high
    @pytest.mark.parametrize(
        "password",
        [
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}!',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}@',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}#',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}$',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}%',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}^',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}&',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}*',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}(',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)})',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)},',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}.',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}?',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}"',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}:',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}' + '{',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}' + '}',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}|',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}<',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}>',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}`',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}~',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}-',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}_',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}=',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}+',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}/',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}\\',
            f"{random_string(1).upper() + random_string(5).lower() + random_digits(1)}'",
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)};',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}[',
            f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)}]'
        ],
        ids=[
            '!',
            '@',
            '#',
            '$',
            '%',
            '^',
            '&',
            '*',
            '(',
            ')',
            ',',
            '.',
            '?',
            '"',
            ':',
            '{',
            '}',
            '|',
            '<',
            '>',
            '`',
            '~',
            '-',
            '_',
            '=',
            '+',
            '/',
            '\\',
            "'",
            ";",
            "[",
            "]"
        ]
    )
    @allure.title('Проверка аутентификации с валидным спецсимволами в password')
    def test_add_user_check_valid_special_chars_in_password(self, get_auth_token, delete_user, password):
        with allure.step('Send request for add user with valid special chars in password'):
            status, response = user.add_user(email=valid_email, password=password, role=role_resp)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code is 201'):
            assert status == HTTP_status.HTTP_201_CREATED
            print('User added')
        with allure.step('Check response'):
            assert 'id' in response
        with allure.step('Postconditions: Delete user'):
            access_token = get_auth_token(email=valid_email, password=password)
            delete_user(password=password, token=access_token)

    @pytest.mark.high
    @pytest.mark.parametrize(
        ('password', 'error'),
        [
            (f'{random_string(6).upper() + random_digits(1)}!', [error_responses.ERROR_PASSWORD_WITHOUT_LOWER]),
            (f'{random_string(6).lower() + random_digits(1)}!', [error_responses.ERROR_PASSWORD_WITHOUT_UPPER]),
            (
                    f'{random_string(1).upper() + random_string(4).lower() + random_digits(1)}!',
                    [error_responses.ERROR_PASSWORD_TOO_SHORT]
            ),
            (
                    f'{random_string(1).upper() + random_string(98).lower() + random_digits(1)}!',
                    [error_responses.ERROR_PASSWORD_TOO_LONG]
            ),
            (
                    f'{random_string(1).upper() + random_string(997).lower() + random_digits(1)}!',
                    [error_responses.ERROR_PASSWORD_TOO_LONG]
            ),
            (
                    f'{random_string(1).upper() + random_string(6).lower()}!',
                    [error_responses.ERROR_PASSWORD_WITHOUT_NUMBERS]
            ),
            (
                    f'{random_string(1).upper() + random_string(6).lower() + random_digits(1)}',
                    [error_responses.ERROR_PASSWORD_WITHOUT_SPECIALS]
            ),
            (
                    f'{random_digits(7)}!',
                    [error_responses.ERROR_PASSWORD_WITHOUT_UPPER, error_responses.ERROR_PASSWORD_WITHOUT_LOWER]
            ),
            ('龍門大酒家龍門大酒家hD1!', [error_responses.ERROR_PASSWORD_NOT_LATIN]),
            ('hD1!صسغذئآ', [error_responses.ERROR_PASSWORD_NOT_LATIN]),
            (
                    f'{random_digits(8)}',
                    [
                        error_responses.ERROR_PASSWORD_WITHOUT_UPPER, error_responses.ERROR_PASSWORD_WITHOUT_LOWER,
                        error_responses.ERROR_PASSWORD_WITHOUT_SPECIALS
                    ]
            ),
            (
                    f'{random_string(1).upper() + random_string(1).lower() + random_digits(1) + random_cyrillics(4)}!',
                    [error_responses.ERROR_PASSWORD_NOT_LATIN]
            ),
            (
                    f'{random_string(1).upper() + random_string(5).lower() + random_digits(1)} !',
                    [error_responses.ERROR_PASSWORD_WITH_WHITESPACE]
            ),
            (" ", [error_responses.ERROR_EMPTY_FIELD]),
            (
                    f'{random_special(8)}',
                    [
                        error_responses.ERROR_PASSWORD_WITHOUT_UPPER, error_responses.ERROR_PASSWORD_WITHOUT_LOWER,
                        error_responses.ERROR_PASSWORD_WITHOUT_NUMBERS
                    ]
            ),
            (
                    random_digits(8),
                    [
                        error_responses.ERROR_PASSWORD_WITHOUT_UPPER, error_responses.ERROR_PASSWORD_WITHOUT_LOWER,
                        error_responses.ERROR_PASSWORD_WITHOUT_SPECIALS
                    ]
            ),
            ('password', [error_responses.ERROR_PASSWORD_TOO_COMMON]),
            (valid_email, [error_responses.ERROR_PASSWORD_EQUAL_EMAIL])
        ],
        ids=[
            'Only upper letters',
            'Only lower letters',
            '7 symbols',
            '101 symbols',
            '1000 symbols',
            'Without numbers',
            'Without specials',
            'Without latin',
            'Group of Chinese',
            'Group of arabic',
            'Only numbers',
            'Group of Cyrillics',
            'include space',
            '1 space',
            'Only specials',
            'Not string',
            'Too common word password',
            'Email in password'
        ]
    )
    @allure.title('Проверка аутентификации с невалидным password')
    def test_add_user_with_invalid_password(self, get_auth_token, delete_user, password, error):
        with allure.step('Send request for add user with invalid password'):
            status, response = user.add_user(email=valid_email, password=password, role=role_resp)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code'):
            if status != HTTP_status.HTTP_201_CREATED:
                assert status == HTTP_status.HTTP_400_BAD_REQUEST
                with allure.step('Check response'):
                    for i in error:
                        assert i in str(response)
            else:
                print('User added')
                access_token = get_auth_token(email=valid_email, password=password)
                delete_user(password=password, token=access_token)


class TestCreateUserModule:
    pass
