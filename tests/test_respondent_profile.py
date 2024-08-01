import pytest
import allure
from faker import Faker
import api
import HTTP_status
import error_responses
from settings import test_user1, random_string, random_digits, random_special, random_cyrillics


auth = api.AuthToken()
user = api.Users()
respondent = api.RespondentProfile()
fake_ru = Faker(['ru_RU'])
fake = Faker(['en-US'])


class TestRespondentProfileBasic:
    @pytest.mark.high
    @pytest.mark.smoke
    @allure.story('Respondent Profile')
    @allure.title('Создание профиля респондента только с обязательными полями базовой анкеты')
    def test_create_base_profile_with_required_fields(self, get_auth_token, delete_respondent_profile):
        # Step 1. Preconditions: get user token
        with allure.step('Preconditions: get user token'):
            access_token = get_auth_token(email=test_user1['email'], password=test_user1['password'])
        # Step 2. Create respondent profile with valid data
        with allure.step('Create respondent profile with valid data'):
            data = {
                "first_name": fake_ru.first_name_male(),
                "last_name": fake_ru.last_name_male(),
                "gender": "мужской",
                "education": "неоконченное среднее",
                "family_status": "одинок/одинока",
                "children": "нет детей",
                "income": "до 10 000",
                "location": "Абаза",
                "date_of_birth": "2013-01-01"
            }
            status, response = respondent.create_profile(token=access_token, data=data)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code is 201'):
            assert status == HTTP_status.HTTP_201_CREATED
        with allure.step("Check profile's data in response"):
            for key in data.keys():
                assert response[key] == data[key]

        # Step 3. Check respondent profile is saved in DB
        with allure.step('Get respondent profile from DB'):
            status, response = respondent.get_profile(token=access_token)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
            assert status == HTTP_status.HTTP_200_OK
            for key in data.keys():
                assert response[key] == data[key]

        # Step 4. Postconditions: Delete respondent profile in DB
        with allure.step('Postconditions: Delete respondent profile in DB'):
            delete_respondent_profile(token=access_token)

    @pytest.mark.high
    @pytest.mark.smoke
    @allure.story('Respondent Profile')
    @allure.title('Создание профиля респондента со всеми полями базовой анкеты')
    def test_create_base_profile_with_all_fields(self, get_auth_token, delete_respondent_profile):
        # Step 1. Preconditions: get user token
        with allure.step('Preconditions: get user token'):
            access_token = get_auth_token(email=test_user1['email'], password=test_user1['password'])
        # Step 2. Create respondent profile with valid data
        with allure.step('Create respondent profile with valid data'):
            data = {
                "first_name": fake_ru.first_name_female(),
                "last_name": fake_ru.last_name_female(),
                "phone_number": "+79123456780",
                "whatsapp": "+79123456780",
                "telegram": "@Women",
                "location": "Абакан",
                "gender": "женский",
                "education": "среднее",
                "family_status": "женат/замужем",
                "children": "1 ребенок",
                "income": "от 10 000 до 20 000",
                "date_of_birth": "1933-01-01",
                "interest_area": [
                    {
                        "title": "авто и мото"
                    }
                ]
            }
            status, response = respondent.create_profile(token=access_token, data=data)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code is 201'):
            assert status == HTTP_status.HTTP_201_CREATED
        with allure.step("Check profile's data in response"):
            for key in data.keys():
                if key != "interest_area":
                    assert response[key] == data[key]
                else:
                    title = data[key][0]
                    assert title['title'] in str(response[key])

        # Step 3. Check respondent profile is saved in DB
        with allure.step('Get respondent profile from DB'):
            status, response = respondent.get_profile(token=access_token)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
            assert status == HTTP_status.HTTP_200_OK
            for key in data.keys():
                if key != "interest_area":
                    assert response[key] == data[key]
                else:
                    title = data[key][0]
                    assert title['title'] in str(response[key])

        # Step 4. Postconditions: Delete respondent profile in DB
        with allure.step('Postconditions: Delete respondent profile in DB'):
            delete_respondent_profile(token=access_token)


class TestRespondentProfileValidation:
    @pytest.mark.high
    @pytest.mark.parametrize(
        ("first_name", "last_name"),
        [
            (f'{random_string(1).upper()}', f'{random_string(1).upper()}'),
            (f'{random_cyrillics(1).upper()}', f'{random_cyrillics(1).upper()}'),
            (f'{fake_ru.first_name()}', f'{fake_ru.last_name()}'),
            (f'{fake.first_name()}', f'{fake.last_name()}'),
            (
                    f'{fake_ru.first_name() + " " + fake_ru.first_name()}',
                    f'{fake_ru.last_name() + " " + fake_ru.last_name()}'
            ),
            (f'{fake.first_name() + " " + fake.first_name()}', f'{fake.last_name() + " " + fake.last_name()}'),
            (
                    f'{fake_ru.first_name() + "-" + fake_ru.first_name()}',
                    f'{fake_ru.last_name() + "-" + fake_ru.last_name()}'
            ),
            (f'{fake.first_name() + "-" + fake.first_name()}', f'{fake.last_name() + "-" + fake.last_name()}'),
            (
                    f'{fake_ru.first_name() + " " + fake_ru.first_name() + " " + fake_ru.first_name()}',
                    f'{fake_ru.last_name() + " " + fake_ru.last_name() + " " + fake_ru.last_name()}'
            ),
            (
                    f'{fake.first_name() + " " + fake.first_name() + " " + fake.first_name()}',
                    f'{fake.last_name() + " " + fake.last_name() + " " + fake.last_name()}'
            ),
            (
                    f'{fake_ru.first_name() + " " + fake_ru.first_name() + "-" + fake_ru.first_name()}',
                    f'{fake_ru.last_name() + " " + fake_ru.last_name() + "-" + fake_ru.last_name()}'
            ),
            (
                    f'{fake.first_name() + " " + fake.first_name() + "-" + fake.first_name()}',
                    f'{fake.last_name() + " " + fake.last_name() + "-" + fake.last_name()}'
            ),
            (f'{fake_ru.first_name()} {fake_ru.middle_name()}', f'{fake_ru.last_name()}'),
            (f'{fake_ru.first_name()} {fake.first_name()}', f'{fake_ru.last_name()} {fake.last_name()}'),
            (f'{fake_ru.first_name()}ё', f'{fake_ru.last_name()}ё'),
            (f'{fake_ru.first_name()}Ё', f'{fake_ru.last_name()}Ё'),
            (f'{random_string(5).upper()}', f'{random_string(5).upper()}'),
            (f'{random_string(5).lower()}', f'{random_string(5).lower()}'),
            (f'{fake_ru.first_name()} {random_digits(1)}', f'{fake_ru.last_name()} {random_digits(1)}'),
            (f'{random_string(100)}', f'{random_string(100)}')
        ],
        ids=[
            '1 symbol latin',
            '1 symbol cyrillic',
            'Russian name',
            'English name',
            'Double russian name with whitespace',
            'Double english name with whitespace',
            'Double russian name with hyphen',
            'Double english name with hyphen',
            'Multiple russian name with whitespaces',
            'Multiple english name with whitespaces',
            'Multiple russian name with whitespaces and hyphen',
            'Multiple english name with whitespaces and hyphen',
            'Russian FIO',
            'Russian and english name',
            'Russian name with ё',
            'Russian name with Ё',
            'Only upper letters',
            'Only lower letters',
            'Letters with number',
            '100 symbols'
        ]
    )
    @allure.title('Проверка валидных значений first_name, last_name')
    def test_first_name_and_last_name_with_valid_data(
            self, get_auth_token, delete_respondent_profile, first_name, last_name
    ):
        # Step 1. Preconditions: get user token
        with allure.step('Preconditions: get user token'):
            access_token = get_auth_token(email=test_user1['email'], password=test_user1['password'])
        # Step 2. Create respondent profile with valid data
        with allure.step('Create respondent profile with valid data in first_name, last_name'):
            data = {
                "first_name": first_name,
                "last_name": last_name,
                "gender": "мужской",
                "education": "неоконченное среднее",
                "family_status": "одинок/одинока",
                "children": "нет детей",
                "income": "до 10 000",
                "location": "Абаза",
                "date_of_birth": "2013-01-01"
            }
            status, response = respondent.create_profile(token=access_token, data=data)
            print(f"\nCode: {status}")
            print(f"Response: {response}")
        with allure.step('Check status code is 201'):
            assert status == HTTP_status.HTTP_201_CREATED
        with allure.step("Check profile's data in response"):
            assert response["first_name"] == first_name
            assert response["last_name"] == last_name

        # Step 3. Postconditions: Delete respondent profile in DB
        with allure.step('Postconditions: Delete respondent profile in DB'):
            delete_respondent_profile(token=access_token)
