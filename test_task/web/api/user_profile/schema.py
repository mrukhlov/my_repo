from pydantic import BaseModel, ConfigDict


class UserProfileModelDTO(BaseModel):
    """
    DTO for user_profile models.

    It returned when accessing user_profile models from the API.
    """

    id: int
    user_id: int
    bio: str
    avatar_url: str
    location: str
    model_config = ConfigDict(from_attributes=True)


class UserProfileModelInputDTO(BaseModel):
    """DTO for creating new user_profile model."""

    user_id: int
    bio: str = ""
    avatar_url: str = ""
    location: str = ""
