from asyncio import AbstractEventLoop
from typing import Optional

import aio_pika
from aio_pika.abc import AbstractRobustConnection
from aio_pika.exceptions import CONNECTION_EXCEPTIONS
from aio_pika.pool import Pool
from loguru import logger

from test_task.settings import settings


async def get_connection() -> AbstractRobustConnection:
    """Function for creatimg rmw connection.

    :returns: queue connection
    """
    try:
        return await aio_pika.connect_robust(str(settings.rabbit_url))
    except CONNECTION_EXCEPTIONS:
        logger.error("Failed to connect to rabbit")
        exit(100)  # noqa: WPS421


class TestTaskQueueConnection:
    """Connect to queue."""

    _channel_pool: Optional[Pool[aio_pika.Channel]] = None

    @classmethod
    async def create(
        cls,
        loop: Optional[AbstractEventLoop] = None,
    ) -> Pool[aio_pika.Channel]:
        """Creates connection pool..

        :param loop: pool that is recreated if passed
        :returns: channel pool
        """
        if cls._channel_pool and not loop:
            return cls._channel_pool

        connection_pool: Pool[aio_pika.connection.Connection] = Pool(
            get_connection,
            max_size=settings.rabbit_pool_size,
            loop=loop,
        )

        async def get_channel() -> aio_pika.Channel:  # noqa: WPS430
            async with connection_pool.acquire() as connection:
                return await connection.channel()  # type: ignore

        cls._channel_pool = Pool(
            get_channel,
            max_size=settings.rabbit_channel_pool_size,
            loop=loop,
        )

        return cls._channel_pool

    @classmethod
    async def close_pool(cls) -> None:
        """Closes pool."""
        if cls._channel_pool is not None:
            await cls._channel_pool.close()
            cls._channel_pool = None
