import json

import mysql.connector
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pickle

from databases.mysql_db import client_mysqldb


class EngineOfDionysus:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def vectorization_of_text(self, tags: str):
        return self.model.encode(tags)

    @staticmethod
    def get_match_polls(list_of_arrays: list[np.ndarray], user_vector: np.ndarray, num_of_polls):
        similarities = cosine_similarity([user_vector], list_of_arrays)
        recommended_doc_ids = np.argsort(similarities[0])[::-1][:num_of_polls]

        return recommended_doc_ids, similarities

    def set_vectorization_of_poll(self, id_of_poll: int):
        try:
            tags_of_poll = client_mysqldb.get_polls_tags(id_of_poll)
            vector_of_poll = self.vectorization_of_text(tags_of_poll)

            vector_of_poll_in_blob = pickle.dumps(vector_of_poll)

            client_mysqldb.create_entry_into_ranking_table(id_of_poll, vector_of_poll_in_blob)

            return json.dumps({'response': 'OK'})

        except AssertionError:
            return json.dumps({'response': '1: Not found the poll'})
        except mysql.connector.IntegrityError:
            return json.dumps({'response': "2: Poll is exists in table"})

    def get_similar_polls(self, id_of_poll, num_of_polls):
        vectorization_polls = [[vectorization_poll[0], pickle.loads(vectorization_poll[1])] for vectorization_poll in client_mysqldb.get_vectorization_polls(id_of_poll)]



