import random
import string

# valid_email = 'test7@khg.ru'
# valid_password = 'String123!'
role_resp = 'respondent'
role_researcher = 'researcher'
non_existent_email = "non_existent@mail.com"
non_existent_password = 'Non.existent.pass123!'


def random_string(length):
    letters = string.ascii_letters
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


def random_digits(length):
    digits = string.digits
    rand_digits = ''.join(random.choice(digits) for i in range(length))
    return rand_digits


def random_special(length):
    specials = string.punctuation
    rand_special = ''.join(random.choice(specials) for i in range(length))
    return rand_special


def random_cyrillics(length):
    cyrillics = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    rand_cyrillics = ''.join(random.choice(cyrillics) for i in range(length))
    return rand_cyrillics


valid_email = random_string(7).lower() + '@' + random_string(5).lower() + '.ru'
valid_password = random_string(1).upper() + random_string(5).lower() + random_digits(1) + '!'


test_user1 = {
    "role": "respondent",
    "email": "user1_for_tests@mail.com",
    "password": "pass123!Q",
    "id": 5
}

test_user2 = {
    "role": "researcher",
    "email": "user2_for_tests@mail.com",
    "password": "pass456!Q",
    "id": 10
}
