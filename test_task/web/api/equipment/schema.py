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
    model_config = ConfigDict(from_attributes=True)


class EquipmentModelInputDTO(BaseModel):
    """DTO for creating new equipment model."""

    name: str
    type: str
    character_id: int
    power: int = 0
    slot: str
    equipped: bool = False
