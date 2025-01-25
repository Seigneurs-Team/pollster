from dataclasses import dataclass
from random import randint


@dataclass
class Poll:
    name_of_poll: str
    description: str
    tags: str
    id_of_poll: int


@dataclass
class Question(Poll):
    id_of_question: int
    text_of_question: str
    type_of_question: str


@dataclass
class Option(Question):
    id_of_option: int
    option: str


@dataclass
class RightAnswer(Option):
    RightAnswerId: int