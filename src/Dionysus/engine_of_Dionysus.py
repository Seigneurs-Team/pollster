import json

import mysql.connector
from transformers import AutoTokenizer, TFAutoModel
from tensorflow import cast, expand_dims, float32, reduce_sum, maximum, math, clip_by_value, linalg
from tensorflow.python.framework.ops import EagerTensor
import numpy as np
import pickle

from databases.mysql_db import client_mysqldb

from Configs.Responses_from_consumer import Responses

import logging

logger = logging.getLogger()


class EngineOfDionysus:
    """
    Класс представляет собой интерфейс для взаимодействия с моделью all-MiniLM-L6-v2
    """
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('/root/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf/')
        self.model = TFAutoModel.from_pretrained('/root/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf/')

    @staticmethod
    def mean_polling(model_output, attention_mask):
        """
        Функция нужна для усреднения значения вывода модели
        :param model_output:
        :param attention_mask:
        :return:
        """
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = cast(expand_dims(attention_mask, -1), float32) * token_embeddings
        return reduce_sum(input_mask_expanded, axis=1) / maximum(reduce_sum(cast(attention_mask, float32)), 1e-3)

    def vectorization_of_text(self, tags: list[str]):
        """
        Функция нужна для нахождения вектора тегов
        :param tags: список тегов
        :return:
        """
        encoded_input = self.tokenizer(tags, padding=True, truncation=True, return_tensors='tf')
        model_output = self.model(**encoded_input)

        sentence_embedding = self.mean_polling(model_output, encoded_input['attention_mask'])
        sentence_embedding = math.l2_normalize(sentence_embedding, axis=1)
        return sentence_embedding

    @staticmethod
    def cosine_similarity(user_vector: EagerTensor, poll_vectors: list[EagerTensor], axis=-1, eps=1e-3):
        """
        Функция нужна для нахождения максимально приближенных векторов к user_vector
        :param user_vector: вектор тегов пользователя
        :param poll_vectors: список векторов опросов
        :param axis: плоскость
        :param eps: значение смещения
        :return:
        """
        list_of_cosine_sim: list = []
        for x2_element in poll_vectors:
            x1_normalize = math.l2_normalize(user_vector, axis=axis)
            x2_normalize = math.l2_normalize(x2_element, axis=axis)

            cosine_sim = linalg.matmul(x1_normalize, x2_normalize, transpose_b=True)
            cosine_sim = clip_by_value(cosine_sim, -1.0 + eps, 1.0 - eps)
            list_of_cosine_sim.append(cosine_sim.numpy()[0][0])

        return np.argsort(list_of_cosine_sim)[::-1]

    def get_match_polls(self, list_of_arrays: list[EagerTensor], user_vector: EagerTensor, num_of_polls):
        """
        Функция возвращает подходящие опросы для конкретного пользователя
        :param list_of_arrays: список векторов опроса
        :param user_vector: вектор пользователя
        :param num_of_polls: количество опросов, которые необходимо вернуть
        :return: список идентификаторов опросов
        """
        recommended_doc_ids = self.cosine_similarity(user_vector, list_of_arrays)[:num_of_polls]
        return recommended_doc_ids

    def set_vectorization_of_poll(self, id_of_poll: int):
        """
        Функция нужна для векторизации тегов опроса, а далее создания или обновления записи в БД.
        :param id_of_poll: идентификатор опроса
        :return: Responses.NotFoundPoll, Responses.PollIsExists, Responses.NotValidData
        """
        try:
            tags_of_poll = client_mysqldb.get_polls_tags(id_of_poll)

            vector_of_poll = self.vectorization_of_text([" ".join(tags_of_poll)])

            vector_of_poll_in_blob = pickle.dumps(vector_of_poll)

            client_mysqldb.create_entry_into_ranking_table(id_of_poll, vector_of_poll_in_blob)

            return json.dumps({'response': Responses.Ok})

        except AssertionError:
            return {'response': Responses.NotFoundPoll}
        except mysql.connector.IntegrityError:
            return {'response': Responses.PollIsExists}
        except TypeError:
            return {'response': Responses.NotValidData}

    def get_similar_polls(self, id_of_user, num_of_polls):
        """
        Функция нужна для нахождения подходящих опросов для пользователя
        :param id_of_user: идентификатор пользователя
        :param num_of_polls: количество опросов
        :return: идентификаторы опросов или Responses.UserPassAllPolls
        """
        try:
            vectorization_polls = [[vectorization_poll[0], pickle.loads(vectorization_poll[1])] for vectorization_poll in client_mysqldb.get_vectorization_polls(id_of_user)]
            vectors = [vector[1] for vector in vectorization_polls]

            vector_of_user = pickle.loads(client_mysqldb.get_vector_of_user(id_of_user))

            recommended_ids = self.get_match_polls(vectors, vector_of_user, num_of_polls)

            return {'response': Responses.Ok, 'polls_ids': [vectorization_polls[idx][0] for idx in recommended_ids]}
        except AssertionError:
            return {'response': Responses.UserPassAllPolls}

    def set_vectorization_user(self, id_of_user):
        """
        Функция нужна для создания или обновления вектора тегов пользователя

        :param id_of_user: идентификатор пользователя
        :return: Responses.Ok, Responses.UserIsExists, Responses.NotFoundUser, Responses.NotValidData
        """
        try:
            tags_of_user = client_mysqldb.get_tags_of_user(id_of_user)
            vector_of_user = self.vectorization_of_text(tags_of_user)

            vector_of_user_in_blob = pickle.dumps(vector_of_user)

            client_mysqldb.add_entry_in_ranking_table_of_users(id_of_user, vector_of_user_in_blob)

            return {'response': Responses.Ok}

        except mysql.connector.IntegrityError:
            return {'response': Responses.UserIsExists}
        except AssertionError:
            return {'response': Responses.NotFoundUser}
        except TypeError:
            return {'response': Responses.NotValidData}




