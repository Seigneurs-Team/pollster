import re

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from typing import Any
from Tools_for_rabbitmq.Queue import Queue
from Configs.Hosts import Hosts
import logging
from logging import basicConfig
from Dionysus.engine_of_Dionysus import EngineOfDionysus

from Configs.Commands_For_RMQ import Commands
basicConfig(filename='consumer.log', filemode='w', level=logging.DEBUG, format='[%(levelname)s] - %(funcName)s - %(message)s')
logger = logging.getLogger()


class Consumer:
    def __init__(self, host):
        self.parameters = pika.ConnectionParameters(heartbeat=60, host=host)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

        self.engine_of_dionysus = EngineOfDionysus()

        self.queue = Queue.poll_queue
        self.queue_callback = Queue.poll_queue_callback
        self.exchange = ''

        self.declare_queue()

        self.consume()
        self.channel.start_consuming()

    def declare_queue(self):
        self.channel.queue_declare(queue=self.queue, durable=True)
        self.channel.queue_declare(queue=self.queue_callback, durable=True)

    def callback(self, channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: Any):
        self.confirm_the_request(channel, method, properties, body)

    def consume(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue, on_message_callback=self.callback)
        self.channel.start_consuming()

    def confirm_the_request(self, channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        result: str = ''
        if re.search(Commands.get_vector_poll, body.decode()):
            result = self.engine_of_dionysus.set_vectorization_of_poll(id_of_poll=int(body.decode().split('=')[1]))
        elif re.search(Commands.get_similar_polls, body.decode()):
            pass
        logger.info(f'Получил сообщение: {body.decode()}')
        channel.basic_publish(
            exchange=self.exchange,
            routing_key=properties.reply_to,
            body=str(result).encode(),
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def callback_on_ping_request(self, channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: Any):
        channel.basic_publish(
            exchange=self.exchange,
            routing_key=properties.reply_to,
            body='pong'.encode()
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def publish(self, body: bytes):
        self.channel.basic_publish(self.exchange, routing_key=self.queue_callback, body=body)

    def reconnect(self):
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()


consumer = Consumer(Hosts.rabbitmq)
