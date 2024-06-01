from loguru import logger

from test_task.db.dao.equipment_dao import EquipmentDAO
from test_task.web.api.equipment.schema import EquipmentRMQMessageSchema
from test_task.workers.base_worker import BaseWorker, run


class EquipItemWorker(BaseWorker):  # noqa: WPS338
    """Worker class working with db."""

    dao_class = EquipmentDAO

    @property
    def name(self) -> str:
        """Worker name.

        :returns: worker name
        """
        return "equip_worker"

    @property
    def queue_name(self) -> str:
        """Returns RabbitMQ queue name.

        :returns: queue name
        """
        return "queue_equip_item"

    @property
    def routing_key(self) -> str:
        """
        Returns routing key to bind exchange and queue.

        :returns: routing key
        """
        return "rtk_equip_item"

    @property
    def message_class(self) -> EquipmentRMQMessageSchema:
        """
        Returns message class to validate and process message.

        :returns: message schema
        """
        return EquipmentRMQMessageSchema  # type: ignore

    async def process(self, data: EquipmentRMQMessageSchema) -> None:  # type: ignore # noqa: 501
        """
        Process incoming data.

        :param data: message json data.
        """
        logger.info("Processing EquipItem message data.")
        logger.info(f"Incoming data: {data}")
        action = data.action
        if action == "equip":
            await self.dao.equip_item(data=data)
        if action == "unequip":
            await self.dao.unequip_item(data=data)


def main() -> None:
    """Runs equip item worker."""
    worker = EquipItemWorker()

    logger.debug("Start equip item worker.")
    run(worker)


if __name__ == "__main__":
    main()
