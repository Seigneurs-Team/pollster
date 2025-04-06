import asyncio
from src.Tools_for_rabbitmq.producer import producer
from src.Tools_for_rabbitmq.Queue import Queue


async def ping_the_consumer():
    """
    Функция представляет собой бесконечный цикл отправки сообщения ping в очередь ping_queue для поддерживания жизни
    подключения Consumer к rabbitmq контейнеру

    :return: None
    """
    while True:
        result = producer.publish('ping', queue=Queue.ping_queue)
        if result is None:
            print('unsuccessful ping requests')
            break
        else:
            await asyncio.sleep(30)
            continue


if __name__ == '__main__':
    asyncio.run(ping_the_consumer())