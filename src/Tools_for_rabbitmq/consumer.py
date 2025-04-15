import json
import re

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from typing import Any
from Tools_for_rabbitmq.Queue import Queue
from Configs.Hosts import Hosts
import logging
from logging import basicConfig
import sys

if '--log_enable' not in sys.argv:
    from Dionysus.engine_of_Dionysus import EngineOfDionysus

from log_system.LogEngine import log_engine

from Configs.Commands_For_RMQ import Commands
basicConfig(filename='consumer.log', filemode='w', level=logging.DEBUG, format='[%(levelname)s] - %(funcName)s - %(message)s')
logger = logging.getLogger()


class Consumer:
    """
    Класс является интерфейсом взаимодействия с rabbbitmq контейнером, как consumer сущность
    """
    def __init__(self, host):
        self.parameters = pika.ConnectionParameters(heartbeat=0, host=host)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

        print('START CONSUMING')
        if '--log_enable' not in sys.argv:
            self.engine_of_dionysus = EngineOfDionysus()

        self.queue = Queue.poll_queue
        self.queue_callback = Queue.poll_queue_callback
        self.log_queue = Queue.log_queue
        self.exchange = ''

        self.declare_queue()

        self.consume()
        self.channel.start_consuming()

    def declare_queue(self):
        if '--log_enable' not in sys.argv:
            self.channel.queue_declare(queue=self.queue, durable=True)
            self.channel.queue_declare(queue=self.queue_callback, durable=True)
        else:
            self.channel.queue_declare(queue=self.log_queue, durable=True)

    def callback(self, channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: Any):
        self.confirm_the_request(channel, method, properties, body)

    def consume(self):
        self.channel.basic_qos(prefetch_count=25)
        if '--log_enable' not in sys.argv:
            self.channel.basic_consume(queue=self.queue, on_message_callback=self.callback)
        else:
            self.channel.basic_consume(queue=self.log_queue, on_message_callback=self.callback_on_log_request)
        self.channel.start_consuming()

    def confirm_the_request(self, channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        """
        Функция исполняет команды, которые присылает Publisher. Команды можно посмотреть в классе Commands Configs.Commands_For_RMQ
        :param channel: канал связи
        :param method: метод доставки сообщения
        :param properties: настройки
        :param body: сообщение в виде байтовой строки
        :return: None
        """
        result: str = ''
        if re.search(Commands.get_vector_poll.replace('%s', ''), body.decode()):
            id_of_poll = int(body.decode().split('=')[1])
            logger.info(id_of_poll)
            logger.info(type(id_of_poll))
            result = self.engine_of_dionysus.set_vectorization_of_poll(id_of_poll=id_of_poll)
        elif re.search(Commands.get_similar_polls.replace('%s', '').split('=')[0], body.decode()):
            num_of_polls = int(re.findall(r'(\d+)', body.decode())[0])
            id_of_user = int(re.findall(r'(-?\d+)', body.decode())[1])

            logger.info("num_of_poll=%s" % num_of_polls)
            logger.info("id_of_user=%s" % id_of_user)

            result = self.engine_of_dionysus.get_similar_polls(id_of_user=id_of_user, num_of_polls=num_of_polls)
        elif re.search(Commands.get_vector_user.replace('%s', ''), body.decode()):
            id_of_user = int(body.decode().split('=')[1])
            result = self.engine_of_dionysus.set_vectorization_user(id_of_user)
        logger.info(f'Получил сообщение: {body.decode()}')
        logger.info(f"Отправляю ответ: {result}")
        channel.basic_publish(
            exchange=self.exchange,
            routing_key=properties.reply_to,
            body=str(json.dumps(result, ensure_ascii=False)).encode(),
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def callback_on_log_request(self, channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        body = str(body.decode())
        level = body.split("$LEVEL=")[1]
        message = json.loads(body.split("$LEVEL=")[0].split('SAVE_LOG_MESSAGE=')[1])
        logger.info(message)

        response = log_engine.create_entry(level, message)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def callback_on_ping_request(self, channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: Any):
        """
        Callback на сообщение ping
        :param channel: канал связи
        :param method: метод доставки сообщения
        :param properties: настройки
        :param body: сообщение в виде байтовой строки
        :return: None
        """
        channel.basic_publish(
            exchange=self.exchange,
            routing_key=properties.reply_to,
            body='pong'.encode()
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def publish(self, body: bytes):
        """
        Отправка Publisher какого-то сообщения
        :param body: сообщение
        :return: None
        """
        self.channel.basic_publish(self.exchange, routing_key=self.queue_callback, body=body)

    def reconnect(self):
        """
        Переподключение к контейнеру rabbitmq

        :return:
        """
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()


consumer = Consumer(Hosts.rabbitmq)
