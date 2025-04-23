from dataclasses import dataclass


@dataclass
class Hosts:
    domain: str = '127.0.0.1'
    mongodb: str = 'localhost'
    mysql_db: str = '172.16.235.2'     #172.16.235.2
    rabbitmq: str = '172.16.235.3'      #172.16.235.3