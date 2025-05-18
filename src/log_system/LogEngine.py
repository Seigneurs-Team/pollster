import zoneinfo
from datetime import datetime
from zoneinfo import ZoneInfo
import json
from os.path import exists


class LogEngine:
    def __init__(self):
        self.path = '../data/'

    def create_entry(self, level: str, message):
        data: dict = {
            'date_of_incident': str(datetime.now(ZoneInfo('Europe/Moscow'))),
            'level_of_incident': level,
            'message_of_incident': message,
        }

        self.check_on_clear(self.path + level + ".json")

        with open(self.path + level + ".json", 'r', encoding='utf-8') as file:
                data_of_file = json.load(file)
                data_of_file.append(data)
        with open(self.path + level + ".json", 'w', encoding='utf-8') as file:
            json.dump(data_of_file, file, ensure_ascii=False, indent=4)

        return 'OK'

    @staticmethod
    def check_on_clear(path: str):
        if exists(path) is False:
            with open(path, 'w', encoding='utf-8') as file:
                json.dump([], file, ensure_ascii=False, indent=4)
            return None
        try:
            with open(path, 'r', encoding='utf-8') as file:
                json.load(file)
        except json.JSONDecodeError:
            with open(path, 'w', encoding='utf-8') as file:
                json.dump([], file, ensure_ascii=False, indent=4)


log_engine = LogEngine()

