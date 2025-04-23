from dataclasses import dataclass, field
from typing import Union, Optional


@dataclass
class Poll:
    name_of_poll: str
    description: str
    tags: str
    id_of_poll: int
    id_of_author: Union[None, int]
    nickname_of_author: str
    cover: Union[None, str]


@dataclass
class Question(Poll):
    id_of_question: int
    text_of_question: str
    type_of_question: str
    serial_number: int


@dataclass
class RightTextAnswer(Question):
    text_of_right_answer: str


@dataclass
class Option(Question):
    id_of_option: int
    option: str


@dataclass
class RightAnswer(Question):
    RightAnswerId: int


@dataclass
class SizeOfImage:
    size_of_cover: int = 3072
