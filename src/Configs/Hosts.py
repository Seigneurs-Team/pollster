from dataclasses import dataclass


@dataclass
class Hosts:
    mongodb: str = 'localhost'
    mysql_db: str = 'localhost'
    rabbitmq: str = 'localhost'