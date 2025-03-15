import asyncio
from src.Tools_for_rabbitmq.producer import producer
from src.Tools_for_rabbitmq.Queue import Queue


async def ping_the_parser():
    while True:
        result = producer.publish('ping', queue=Queue.ping_queue)
        if result is None:
            print('unsuccessful ping requests')
            break
        else:
            await asyncio.sleep(30)
            continue