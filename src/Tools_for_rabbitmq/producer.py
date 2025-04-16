import json
import typing

import pika
from typing import Any, Optional, Union
import re
from Tools_for_rabbitmq.Queue import Queue
from pika import exceptions
from Configs.Hosts import Hosts
from Configs.Exceptions import WronglyResponse, ConnectionRefused

from Configs.Responses_from_consumer import Responses

from Configs.Commands_For_RMQ import Commands


class Producer:
    """
    Класс представляет собой интерфейсов работы с rabbitmq контейнером, как Publisher
    """
    def __init__(self, host):
        self.parameters = pika.ConnectionParameters(heartbeat=0, host=host)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

        self.exchange = ''
        self.queue = Queue.poll_queue
        self.callback_queue = Queue.poll_queue_callback
        self.log_queue = Queue.log_queue

        self.declare_queue()
        self.consume_the_response()

        self.response: Optional[str] = None
        self.info_response: Union[str, None] = None

    def declare_queue(self):
        self.channel.queue_declare(queue=self.queue, durable=True)
        self.channel.queue_declare(queue=self.callback_queue, durable=True)
        self.channel.queue_declare(queue=Queue.ping_queue, durable=True)
        self.channel.queue_declare(queue=self.log_queue, durable=True)

    def publish(self, message: Any, properties: pika.BasicProperties = None, queue=None, callback_queue=None):
        """
        Функция отправляет сообщение в очередь queue, Сообщение представляет собой команду.

        :param message: команда для Consumer
        :param properties: настройки передачи
        :param queue: очередь, куда отправляется сообщение
        :param callback_queue: очередь для ожидания ответа
        :return: ответ от Consumer
        """
        properties_with_reply_to = pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent, reply_to=self.callback_queue)
        try:
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.queue if queue is None else queue,
                body=message.encode(),
                properties=properties_with_reply_to if properties is None else properties
            )

            count: int = 0
            while self.response is None:
                if properties is not None:
                    return
                self.connection.process_data_events(time_limit=0.3)
                count += 1
                if count == 5:
                    raise ConnectionRefused('соединение с контейнером потеряно')
            else:
                response = self.response
                self.response = None
                return json.loads(response)
        except (exceptions.ChannelWrongStateError, pika.exceptions.StreamLostError, AssertionError):
            self.reconnect()
            self.publish(message=message, properties=properties, queue=queue)

        except ConnectionRefused:
            return Responses.RefusedConnection

    def publish_log(self, message: str, level: str, id_of_user: Optional[int], requests: Any = None, other_data: dict = None):
        other_data = other_data if other_data is not None else {}
        dict_of_data = (
            {
                'message': message,
                'ip': requests.META["REMOTE_ADDR"] if requests is not None else '',
                'userid': id_of_user,
                'endpoint': requests.path
            }
        )

        for k, v in other_data.items():
            dict_of_data[k] = v

        dict_of_data = json.dumps(dict_of_data)
        message = Commands.save_log % (dict_of_data, level)

        self.publish(message, queue=self.log_queue, properties=pika.BasicProperties(delivery_mode=1))

    def close_connection(self):
        self.channel.close()

    def consume_the_response(self):
        """
        Функция нужна для обозначения ожидания ответа от Consumer в очереди self.callback_queue

        :return: None
        """
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

    def on_response(self, channel, method, properties, body: bytes):
        """
        Callback функция на ответ от Consumer
        :param channel: канал связи
        :param method: метод передачи
        :param properties: настройки передачи
        :param body: сообщение ответа в виде байтов
        :return: None
        """
        if re.search(r'ERROR', body.decode()):
            raise WronglyResponse(f'Ошибка: {body.decode()}')
        else:
            self.response = body.decode()

    def reconnect(self):
        """
        Функция нужна для переподключения к контейнеру rabbitmq

        :return: None
        """
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.declare_queue()
        self.consume_the_response()


producer = Producer(Hosts.rabbitmq)

