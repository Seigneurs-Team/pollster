from PoW.generate_random_string import generate_random_string
from PoW.get_timestamp import get_timestamp
import hashlib


class EnginePoW:
    def __init__(self):
        self.random_string = generate_random_string()
        self.timestamp = get_timestamp()
        self.count_of_bits = 3
        self.version = 1
        self.resource = 'pollster'
        self.extension = ''

    def hash_cash_algorithm(self):
        count = 0

        while True:
            string_for_hash = f"{self.version}:{self.count_of_bits}:{self.timestamp}:{self.resource}:{self.extension}:{self.random_string}:{count}".encode()
            hash_value = hashlib.sha256(string_for_hash).hexdigest()
            if hash_value.startswith('0'*self.count_of_bits):
                return count
            count += 1