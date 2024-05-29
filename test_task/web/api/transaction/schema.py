from typing import Optional

from pydantic import BaseModel, ConfigDict

from test_task.web.api.character.schema import CharacterModelDTO
from test_task.web.api.currency_type.schema import CurrencyTypeModelDTO
from test_task.web.api.equipment.schema import EquipmentModelDTO


class TransactionModelDTO(BaseModel):
    """
    DTO for transaction models.

    It returned when accessing transaction models from the API.
    """

    id: int
    character_from: CharacterModelDTO
    character_to: CharacterModelDTO
    item: Optional[EquipmentModelDTO]
    amount: Optional[int]
    transaction_type: Optional[str]
    currency_type: Optional[CurrencyTypeModelDTO]
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class TransactionModelInputDTO(BaseModel):
    """DTO for creating new transaction model."""

    character_to_id: int
    character_from_id: int
    item_id: int
    amount: int
    transaction_type: str | None = None
    currency_type_id: int
