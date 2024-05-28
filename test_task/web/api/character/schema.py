from pydantic import BaseModel, ConfigDict


class CharacterModelDTO(BaseModel):
    """
    DTO for character models.

    It returned when accessing character models from the API.
    """

    id: int
    name: str
    user_id: int
    level: int
    experience: int
    model_config = ConfigDict(from_attributes=True)


class CharacterModelIDDTO(BaseModel):
    """
    DTO for character models.

    It returned when accessing character models from the API.
    """

    id: int
    model_config = ConfigDict(from_attributes=True)


class CharacterModelInputDTO(BaseModel):
    """DTO for creating new character model."""

    name: str
    user_id: int
    level: int = 1
    experience: int = 0
