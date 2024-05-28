from pydantic import BaseModel, ConfigDict

from test_task.web.api.character.schema import CharacterModelIDDTO


class InventoryModelDTO(BaseModel):
    """
    DTO for inventory models.

    It returned when accessing inventory models from the API.
    """

    id: int
    character: CharacterModelIDDTO
    item_name: str
    item_type: str
    quantity: int
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class InventoryModelInputDTO(BaseModel):
    """DTO for creating new inventory model."""

    character_id: int
    item_name: str
    item_type: str
    quantity: int
