from dataclasses import dataclass


@dataclass
class Hosts:
    mongodb: str = 'localhost'
    mysql_db: str = '172.16.235.2'
    rabbitmq: str = 'localhost'