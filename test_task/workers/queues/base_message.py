import datetime
import json
import uuid

import aio_pika
from loguru import logger
from pydantic import BaseModel

from test_task.settings import settings
from test_task.workers.queues.pool import TestTaskQueueConnection


class TestTaskMessage(BaseModel):
    """Base class for messages that should be sent to rmq."""

    event_created_at: datetime.datetime

    async def publish(
        self,
        routing_key: str,
    ) -> bool:
        """
        Publish message to exchange with routing key.

        :param routing_key: routing key.
        :return: is message pudlished flag.
        """
        try:
            pool = await TestTaskQueueConnection.create()
            async with pool.acquire() as channel:
                exchange = await channel.get_exchange(
                    settings.exchange_name,
                    ensure=False,
                )
                message = "asd"
                await exchange.publish(
                    message=aio_pika.Message(
                        body=json.dumps(message).encode("utf-8"),
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                        headers={
                            "id": str(uuid.uuid4()),
                            "task": routing_key,
                        },
                        content_type="application/json",
                        content_encoding="utf-8",
                    ),
                    routing_key=routing_key,
                )
        except (
            aio_pika.AMQPException,
            aio_pika.MessageProcessError,
            aio_pika.exceptions.ChannelClosed,
        ):
            logger.opt(exception=True).exception(
                "Failed to send message",
                extra={"message": self.json()},
            )
            return False
        return True

    class Config:
        json_encoders = {
            uuid.UUID: lambda unique_id: unique_id.hex,
        }
