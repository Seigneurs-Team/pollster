from dataclasses import dataclass
from random import randint


@dataclass
class Poll:
    description: str
    name_of_poll: str
    tags: str
    id: int
