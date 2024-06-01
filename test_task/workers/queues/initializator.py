from aio_pika import ExchangeType
from loguru import logger

from test_task.settings import settings
from test_task.workers.queues.pool import TestTaskQueueConnection


async def init_exchange() -> None:
    """Creating exchange for messages."""
    channel_pool = await TestTaskQueueConnection.create()
    async with channel_pool.acquire() as channel:
        await channel.declare_exchange(
            settings.exchange_name,
            type=ExchangeType.DIRECT,
            durable=False,
            auto_delete=True,
        )
        logger.debug(f"Created exchange '{settings.exchange_name}'.")


async def add_exchange_binding(
    routing_key: str = "",
    queue_name: str = "",
) -> None:
    """
    Add exchange binding by key.

    :param routing_key: routing key.
    :param queue_name: queue name.
    """
    channel_pool = await TestTaskQueueConnection.create()
    async with channel_pool.acquire() as channel:
        queue = await channel.declare_queue(
            queue_name,
        )
        await queue.bind(
            settings.exchange_name,
            routing_key=routing_key,
        )
        logger.debug(
            f"Created binding '{settings.exchange_name}' -> '{queue_name}'.",
        )
