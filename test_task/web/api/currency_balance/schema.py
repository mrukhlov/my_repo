from pydantic import BaseModel, ConfigDict


class CurrencyBalanceModelDTO(BaseModel):
    """
    DTO for currency_balance models.

    It returned when accessing currency_balance models from the API.
    """

    id: int
    character_id: int
    currency_type_id: int
    balance: int
    model_config = ConfigDict(from_attributes=True)


class CurrencyBalanceModelInputDTO(BaseModel):
    """DTO for creating new currency_balance model."""

    character_id: int
    currency_type_id: int
    amount: int
