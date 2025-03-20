import json

import mysql.connector
from transformers import AutoTokenizer, TFAutoModel
from tensorflow import cast, expand_dims, float32, reduce_sum, maximum, math, clip_by_value
import numpy as np
import pickle

from databases.mysql_db import client_mysqldb

from Configs.Responses_from_consumer import Responses


class EngineOfDionysus:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('all-MiniLM-L6-v2')
        self.model = TFAutoModel.from_pretrained('all-MiniLM-L6-v2')

    @staticmethod
    def cosine_similarity(x1, x2, axis=1, eps=1e-3):
        x1_normalize = math.l2_normalize(x1, axis=axis)
        x2_normalize = math.l2_normalize(x2, axis=axis)

        cosine_sim = reduce_sum(x1_normalize * x2_normalize, axis=axis)
        cosine_sim = clip_by_value(cosine_sim, -1.0+eps, 1.0-eps)

        return cosine_sim.numpy()

    @staticmethod
    def mean_polling(model_output, attention_mask):
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = cast(expand_dims(attention_mask, -1), float32) * token_embeddings
        return reduce_sum(input_mask_expanded, axis=1) / maximum(reduce_sum(cast(attention_mask, float32), 1e-3))

    def vectorization_of_text(self, tags: list[str]):
        encoded_input = self.tokenizer(tags, padding=True, truncation=True, return_tensors='tf')
        model_output = self.model(**encoded_input)

        sentence_embedding = self.mean_polling(model_output, encoded_input['attention_mask'])
        sentence_embedding = math.l2_normalize(sentence_embedding, axis=1)
        return sentence_embedding

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




