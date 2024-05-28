from pydantic import BaseModel, ConfigDict


class UserModelDTO(BaseModel):
    """
    DTO for user models.

    It returned when accessing user models from the API.
    """

    id: int
    username: str
    email: str
    password_hash: str
    model_config = ConfigDict(from_attributes=True)


class UserModelInputDTO(BaseModel):
    """DTO for creating new user model."""

    username: str
    email: str
    password_hash: str
