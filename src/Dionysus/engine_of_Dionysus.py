import json

import mysql.connector
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pickle

from databases.mysql_db import client_mysqldb

from Configs.Responses_from_consumer import Responses


class EngineOfDionysus:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def vectorization_of_text(self, tags: str):
        return self.model.encode(tags)

    @staticmethod
    def get_match_polls(list_of_arrays: list[np.ndarray], user_vector: np.ndarray, num_of_polls):
        similarities = cosine_similarity([user_vector], list_of_arrays)
        recommended_doc_ids = np.argsort(similarities[0])[::-1][:num_of_polls]

        return recommended_doc_ids

    def set_vectorization_of_poll(self, id_of_poll: int):
        try:
            tags_of_poll = client_mysqldb.get_polls_tags(id_of_poll)
            vector_of_poll = self.vectorization_of_text(tags_of_poll)

            vector_of_poll_in_blob = pickle.dumps(vector_of_poll)

            client_mysqldb.create_entry_into_ranking_table(id_of_poll, vector_of_poll_in_blob)

            return json.dumps({'response': Responses.Ok})

        except AssertionError:
            return json.dumps({'response': Responses.NotFoundPoll})
        except mysql.connector.IntegrityError:
            return json.dumps({'response': Responses.PollIsExists})

    def get_similar_polls(self, id_of_user, num_of_polls):
        try:
            vectorization_polls = [[vectorization_poll[0], pickle.loads(vectorization_poll[1])] for vectorization_poll in client_mysqldb.get_vectorization_polls(id_of_user)]
            vectors = [vector[1] for vector in vectorization_polls]

            vector_of_user = pickle.loads(client_mysqldb.get_vector_of_user(id_of_user))

            recommended_ids = self.get_match_polls(vectors, vector_of_user, num_of_polls)

            return json.dumps({'response': Responses.Ok, 'polls_ids': [vectorization_polls[idx][0] for idx in recommended_ids]})
        except AssertionError:
            return json.dumps({'response': Responses.UserPassAllPolls})

    def set_vectorization_user(self, id_of_user):
        try:
            tags_of_user = client_mysqldb.get_tags_of_user(id_of_user)
            vector_of_user = self.vectorization_of_text(" ".join(tags_of_user))

            vector_of_user_in_blob = pickle.dumps(vector_of_user)

            client_mysqldb.add_entry_in_ranking_table_of_users(id_of_user, vector_of_user_in_blob)

            return json.dumps({'response': 'OK'})

        except mysql.connector.IntegrityError:
            return json.dumps({'response': Responses.UserIsExists})
        except AssertionError:
            return json.dumps({'response': Responses.NotFoundUser})



