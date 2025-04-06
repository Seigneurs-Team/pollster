from datetime import datetime


def get_timestamp() -> int:
    """
    Функция нужна для получения текущей даты в виде timestamp

    :return: Timestamp
    """
    return int(datetime.today().timestamp())