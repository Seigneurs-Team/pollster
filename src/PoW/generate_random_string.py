import random
import string


def generate_random_string(length_of_random_string: int = 16) -> str:
    """
    Функция генерирует строку со случайными буквами и цифрами
    :param length_of_random_string:
    :return:
    """
    characters = string.ascii_letters + string.digits
    return_string = ''.join(random.choice(characters) for _ in range(length_of_random_string))

    return return_string