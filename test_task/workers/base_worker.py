import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Callable

import aio_pika
from loguru import logger
from pydantic import ValidationError
from tortoise import Tortoise

from test_task.db.config import TORTOISE_CONFIG
from test_task.workers.queues.initializator import add_exchange_binding, init_exchange
from test_task.workers.queues.pool import TestTaskQueueConnection


class BaseWorker(ABC):  # noqa: WPS230, WPS338
    """
    Base worker.

    Receives messages from rabbitqm  queue,
    processes them and works with db.
    """

    channel_pool: aio_pika.pool.Pool[aio_pika.Channel]
    dao_class: Callable[..., Any]

    @property
    @abstractmethod
    def name(self) -> str:
        """Worker name.

        :returns: worker name.
        """

    @property
    @abstractmethod
    def queue_name(self) -> str:
        """Returns RabbitMQ queue name.

        :raises NotImplementedError: Must be redefined
        """

    @property
    @abstractmethod
    def routing_key(self) -> str:
        """
        Returns routing key to bind exchange and queue.

        :raises NotImplementedError: Must be redefined
        """

    @property
    @abstractmethod
    def message_class(self) -> Any:
        """
        Returns message class to validate and process message.

        :raises NotImplementedError: Must be redefined
        """

    @abstractmethod
    async def process(self, data: Callable[..., Any]) -> None:
        """
        Process incoming data.

        :param data: message json data.
        """

    async def init_db(self) -> None:
        """Initializinf db connection."""
        await Tortoise.init(config=TORTOISE_CONFIG)
        self.db_connection = Tortoise.get_connection("default")
        self.dao = self.dao_class()
        self.dao.using_db = self.db_connection
        logger.debug("Initialized db connection.")

    async def run(
        self,
        event_loop: asyncio.AbstractEventLoop,
    ) -> None:
        """
        Runs worker.

        :param event_loop: event loop need for connection pool
        """
        logger.debug("Worker initialized.")

        await self.init_db()

        await init_exchange()
        await add_exchange_binding(
            self.routing_key,
            self.queue_name,
        )
        self.channel_pool = await TestTaskQueueConnection.create(loop=event_loop)
        logger.debug("Added connection from worker to test_task rabbitmq")

        logger.debug(f"Start listening queue {self.queue_name}")
        while True:  # noqa: WPS457
            await asyncio.wait_for(
                await self.start_listening_queue(),  # type: ignore
                timeout=None,
            )

    async def start_listening_queue(self) -> None:
        """Runs listening process and accepting messages."""
        async with self.channel_pool.acquire() as channel:
            queue = await channel.declare_queue(
                self.queue_name,
            )

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    await self.process_rabbit_message(message)  # type: ignore

    def _is_message_valid(self, message: aio_pika.IncomingMessage) -> bool:
        """
        Validate incoming message.

        :param message: queue message.
        :returns: flag if mesage is valid or not.
        """
        message_body = None
        try:
            message_body = json.loads(message.body.decode("utf-8"))
            self.message_class(  # type: ignore
                **message_body,
            )
        except (
            ValidationError,
            TypeError,
            ValueError,
        ) as err:
            logger.error(
                f"Wrong message format {message_body}.\n" f"Error - {err}",
            )
            return False
        return True

    def _get_message_data(
        self,
        message: aio_pika.IncomingMessage,
    ) -> Callable[..., Any]:
        """
        Receive message info.

        :param message: RabbitMQ message.
        :returns: message data dict.
        """
        return self.message_class(  # type: ignore
            **json.loads(message.body.decode("utf-8")),
        )

    async def process_rabbit_message(
        self,
        message: aio_pika.IncomingMessage,
    ) -> None:
        """
        Receiving and processing message.

        :param message: message
        :returns: None
        """
        async with message.process(requeue=True, ignore_processed=True):
            logger.info("Received a queue message.")

            if not self._is_message_valid(message):
                return

            message_data = self._get_message_data(message)
            await self.process(message_data)


def run(worker: BaseWorker) -> None:
    """Creates event loop and runs worker in it.

    :param worker: worker instance
    """
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(
            worker.run(event_loop),
        )
    except KeyboardInterrupt:
        logger.info("Gracefully stopped.")
    except Exception as ex:
        logger.exception("Event loop error", ex)
    finally:
        event_loop.stop()
