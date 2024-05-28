from pydantic import BaseModel, ConfigDict


class CreateUser(BaseModel):
    """CreateUser model."""

    email: str
    password: str
    username: str
    model_config = ConfigDict(from_attributes=True)


class LoginUser(BaseModel):
    """LoginUser model."""

    email: str
    username: str
    password: str
    model_config = ConfigDict(from_attributes=True)


class UserOutput(BaseModel):
    """UserOutput model."""

    email: str
    username: str
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Token model."""

    access_token: str | None = None
    refresh_token: str | None = None
    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    """TokenData model."""

    exp: int
    email: str
    username: str
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class TokenPayload(BaseModel):
    """TokenPayload model."""

    access_token: str
    token_type: str
    model_config = ConfigDict(from_attributes=True)
