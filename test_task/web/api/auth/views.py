from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status

from test_task.db.models.models import Role, User
from test_task.services.auth.auth import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_user,
    get_hashed_password,
    verify_password,
)
from test_task.web.api.auth.schema import CreateUser, LoginUser, Token, UserOutput

router = APIRouter()


@router.post("/register", response_model=UserOutput)
async def create_user(data: CreateUser) -> UserOutput:
    """
    Create user in database.

    :param data: user data.
    :raises HTTPException: HTTPException.
    :return: user model.
    """
    user = await User.filter(email=data.email).first()
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist",
        )
    role = await Role.get(id=1)
    user = await User.create(
        email=data.email,
        username=data.username,
        password_hash=get_hashed_password(data.password),
        role=role,
    )
    return UserOutput.model_validate(user)


@router.post("/login", response_model=Token)
async def login(form_data: LoginUser) -> Token:
    """
    Login user.

    :param form_data: user data.
    :raises HTTPException: HTTPException.
    :return: access and refresh token.
    """
    user = await User.filter(email=form_data.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    hashed_pass = user.password_hash
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    data = {
        "email": str(user.email),
        "username": str(user.username),
        "user_id": int(user.id),
    }

    token_data = {
        "access_token": create_access_token(data),  # type: ignore
        "refresh_token": create_refresh_token(data),  # type: ignore
    }
    return Token(**token_data)


@router.post("/refresh")
async def refresh_token(token: Token) -> Dict[str, str]:
    """
    Refresh access token.

    :param token: token.
    :raises HTTPException: HTTPException.
    :return: access_token.
    """
    token_data = decode_refresh_token(token.refresh_token)  # type: ignore
    user = await User.get_or_none(id=token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    data = {
        "email": str(user.email),
        "username": str(user.username),
        "user_id": int(user.id),
    }

    new_access_token = create_access_token(data)  # type: ignore

    return {"access_token": new_access_token}


@router.get("/me", response_model=UserOutput)
async def get_me(
    current_user: UserOutput = Depends(get_current_user),
) -> UserOutput:
    """
    Endpoint to get current authenticated user's details.

    :param current_user: current_user.
    :return: current_user.
    """
    return current_user


@router.get("/protected-route", response_model=UserOutput)
async def protected_route(
    current_user: UserOutput = Depends(get_current_user),
) -> UserOutput:
    """
    A protected route that requires the user to be authenticated.

    :param current_user: current_user.
    :return: current_user.
    """
    return current_user
