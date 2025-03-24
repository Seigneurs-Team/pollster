import json

import pika
from typing import Any, Optional, Union
import re
from Tools_for_rabbitmq.Queue import Queue
from pika import exceptions
from Configs.Hosts import Hosts
from Configs.Exceptions import WronglyResponse, ConnectionRefused


class Producer:
    def __init__(self, host):
        self.parameters = pika.ConnectionParameters(heartbeat=0, host=host)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

        self.exchange = ''
        self.queue = Queue.poll_queue
        self.callback_queue = Queue.poll_queue_callback

        self.declare_queue()
        self.consume_the_response()

        self.response: Optional[str] = None
        self.info_response: Union[str, None] = None

    def declare_queue(self):
        self.channel.queue_declare(queue=self.queue, durable=True)
        self.channel.queue_declare(queue=self.callback_queue, durable=True)
        self.channel.queue_declare(queue=Queue.ping_queue, durable=True)

    def publish(self, message: Any, properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent), queue=None, callback_queue=None):
        properties = pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent, reply_to=self.callback_queue)
        try:
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.queue if queue is None else queue,
                body=message.encode(),
                properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent, reply_to=self.callback_queue)
            )

            count: int = 0
            while self.response is None:
                self.connection.process_data_events(time_limit=3)
                count += 1
                if count == 2:
                    raise ConnectionRefused('соединение с контейнером потеряно')
            else:
                response = self.response
                self.response = None
                return json.loads(response)
        except exceptions.ChannelWrongStateError:
            self.reconnect()
            self.publish(message=message, properties=properties, queue=queue)

        except ConnectionRefused:
            return 'Потеряно соединение с сервером Dionysus'

    def close_connection(self):
        self.channel.close()

    def consume_the_response(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

    def on_response(self, channel, method, properties, body: bytes):
        if re.search(r'ERROR', body.decode()):
            raise WronglyResponse(f'Ошибка: {body.decode()}')
        else:
            print(body.decode())
            self.response = body.decode()

    def reconnect(self):
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()


producer = Producer(Hosts.rabbitmq)

