from dataclasses import dataclass


@dataclass
class Commands:
    get_vector_poll = "GET_VECTOR_of_poll=%s"
    get_similar_polls = "GET_SIMILAR_POLLS_NUM=%s$AND_ID_OF_USER=%s"
    get_vector_user = "GET_VECTOR_of_user=%s"

    save_log = "SAVE_LOG_MESSAGE=%s$LEVEL=%s"