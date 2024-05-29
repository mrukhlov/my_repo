from pydantic import BaseModel, ConfigDict


class CurrencyTypeModelDTO(BaseModel):
    """
    DTO for currency_type models.

    It returned when accessing currency_type models from the API.
    """

    id: int
    name: str
    description: str | None = None
    model_config = ConfigDict(from_attributes=True)


class CurrencyTypeModelInputDTO(BaseModel):
    """DTO for creating new currency_type model."""

    name: str
    description: str = ""
