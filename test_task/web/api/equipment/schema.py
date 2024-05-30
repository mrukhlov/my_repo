from pydantic import BaseModel, ConfigDict


class EquipmentModelDTO(BaseModel):
    """
    DTO for equipment models.

    It returned when accessing equipment models from the API.
    """

    id: int
    name: str
    type: str
    character_id: int
    power: int
    slot: str
    equipped: bool
    price: float
    currency_type_id: int
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class EquipmentModelInputDTO(BaseModel):
    """DTO for creating new equipment model."""

    name: str
    type: str
    character_id: int
    power: int = 0
    slot: str
    equipped: bool = False
    price: float = 0.00
    currency_type_id: int


class TransferEquipmentInputDTO(BaseModel):
    """DTO for transfer equpment."""

    character_from: int
    character_to: int
    item_id: int


class EquipmentRMQMessageDTO(BaseModel):
    """DTO for publishing message in RabbitMQ."""

    exchange_name: str
    routing_key: str
    character_id: int
    item_id: int
