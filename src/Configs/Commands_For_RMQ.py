from dataclasses import dataclass


@dataclass
class Commands:
    get_vector_poll = "GET_VECTOR_of_poll=%s"
    get_similar_polls = "GET_SIMILAR_POLLS_NUM=%sAND_ID_OF_POLL=%s"