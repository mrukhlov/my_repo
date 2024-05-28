from datetime import datetime, timedelta
from typing import Dict, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from test_task.db.models.models import User
from test_task.settings import settings
from test_task.web.api.auth.schema import TokenData, UserOutput

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT",
)


ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.refresh_token_expire_minutes
ALGORITHM = settings.algorithm
JWT_SECRET_KEY = settings.jwt_secret_key
JWT_REFRESH_SECRET_KEY = settings.jwt_refresh_secret_key


def get_hashed_password(password: str) -> str:
    """
    Get hashed password.

    :param password: user password.
    :return: hashed password.
    """
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """
    Verify user password.

    :param password: user password.
    :param hashed_pass: user hashed_pass.
    :return: flag if passwords equal.
    """
    return password_context.verify(password, hashed_pass)


def create_access_token(
    data: Dict[str, Union[int, str]],
    expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES,
) -> str:
    """
    Create access token.

    :param data: user data.
    :param expires_delta: expires_delta.
    :return: access token.
    """
    expires_delta = datetime.now() + timedelta(minutes=expires_delta)  # type: ignore

    to_encode = {
        "exp": expires_delta,
        "email": str(data["email"]),
        "username": str(data["username"]),
        "user_id": int(data["user_id"]),
    }
    return jwt.encode(
        to_encode,
        JWT_SECRET_KEY,
        ALGORITHM,
    )


def create_refresh_token(
    data: Dict[str, Union[int, str]],
    expires_delta: int = REFRESH_TOKEN_EXPIRE_MINUTES,
) -> str:
    """
    Create refresh token.

    :param data: user data.
    :param expires_delta: expires_delta.
    :return: refresh token.
    """
    expires_delta = datetime.now() + timedelta(minutes=expires_delta)  # type: ignore

    to_encode = {
        "exp": expires_delta,
        "email": str(data["email"]),
        "username": str(data["username"]),
        "user_id": int(data["user_id"]),
    }

    return jwt.encode(
        to_encode,
        JWT_REFRESH_SECRET_KEY,
        ALGORITHM,
    )


def decode_refresh_token(token: str) -> TokenData:
    """
    Decode refresh token.

    :param token: token.
    :raises HTTPException: HTTPException.
    :return: TokenData model.
    """
    try:
        payload = jwt.decode(token, JWT_REFRESH_SECRET_KEY, algorithms=ALGORITHM)
        return TokenData(**payload)
    except (jwt.ExpiredSignatureError, jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_access_token(token: str) -> TokenData:
    """
    Decode access token.

    :param token: token.
    :raises HTTPException: HTTPException.
    :return: TokenData model.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=ALGORITHM)
        return TokenData(**payload)
    except (jwt.ExpiredSignatureError, jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token_access(token: str) -> TokenData:
    """
    Verify access.

    :param token: user token.
    :raises HTTPException: HTTPException.
    :raises exp: JWTError.
    :return: TokenData model.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=ALGORITHM)
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect user_id",
            )
        return TokenData(**payload)
    except jwt.JWTError as exp:  # noqa: WPS329
        raise exp


async def get_current_user(token: str = Depends(reuseable_oauth)) -> UserOutput:
    """
    Method to check auth header.

    :param token: user token.
    :raises HTTPException: HTTPException.
    :return: User model.
    """
    try:
        token_data = verify_token_access(token)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await User.filter(
        id=token_data.user_id,
        username=token_data.username,
        email=token_data.email,
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated",
        )

    return UserOutput.model_validate(user)
