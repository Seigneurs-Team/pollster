from dataclasses import dataclass
from random import randint


@dataclass
class Poll:
    name_of_poll: str
    description: str
    tags: str
    id: int
