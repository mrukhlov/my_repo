import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture
from starlette import status

from test_task.db.models.models import Role, User


@pytest.mark.anyio
async def test_register_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_role: Role,
) -> None:
    """Tests user register."""
    url = fastapi_app.url_path_for("create_user")
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "username": "testuser",
    }

    response = await client.post(url, json=user_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


@pytest.mark.anyio
async def test_register_existing_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_user: User,
    create_role: Role,
) -> None:
    """Tests register existing user."""
    url = fastapi_app.url_path_for("create_user")
    user_data = {
        "email": create_user.email,
        "password": "testpassword",
        "username": "testuser",
    }

    response = await client.post(url, json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "User with this email already exist"


@pytest.mark.anyio
async def test_login_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_user: User,
    create_role: Role,
    mocked_verify_password: MockerFixture,
) -> None:
    """Tests user login."""
    url = fastapi_app.url_path_for("login")
    login_data = {
        "email": create_user.email,
        "password": create_user.password_hash,
        "username": create_user.username,
    }

    response = await client.post(url, json=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.anyio
async def test_login_invalid_user(
    client: AsyncClient,
    fastapi_app: FastAPI,
    create_role: Role,
) -> None:
    """Tests login invalid user."""
    url = fastapi_app.url_path_for("login")
    login_data = {
        "email": "invalid@example.com",
        "password": "wrongpassword",
        "username": "invaliduser",
    }

    response = await client.post(url, json=login_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.anyio
async def test_refresh_token(
    client: AsyncClient,
    fastapi_app: FastAPI,
    mocked_verify_password: MockerFixture,
    create_user: User,
    create_role: Role,
    create_refresh_token: str,
) -> None:
    """Tests refresh token."""
    url = fastapi_app.url_path_for("login")
    login_data = {
        "email": create_user.email,
        "password": create_user.password_hash,
        "username": create_user.username,
    }

    response = await client.post(url, json=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    url = fastapi_app.url_path_for("refresh_token")
    refresh_data = {"refresh_token": data["refresh_token"]}

    response = await client.post(url, json=refresh_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data


@pytest.mark.anyio
async def test_refresh_token_invalid(
    client: AsyncClient,
    fastapi_app: FastAPI,
    create_role: Role,
) -> None:
    """Tests invalid token refresh."""
    url = fastapi_app.url_path_for("refresh_token")
    refresh_data = {"refresh_token": "invalid_refresh_token_here"}

    response = await client.post(url, json=refresh_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Could not validate credentials"


@pytest.mark.anyio
async def test_get_me(
    client: AsyncClient,
    fastapi_app: FastAPI,
    mocked_verify_password: MockerFixture,
    create_user: User,
    create_role: Role,
    create_refresh_token: str,
) -> None:
    """Tests get_me handler with auth header."""
    url = fastapi_app.url_path_for("login")
    login_data = {
        "email": create_user.email,
        "password": create_user.password_hash,
        "username": create_user.username,
    }

    response = await client.post(url, json=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    url = fastapi_app.url_path_for("get_me")
    headers = {
        "Authorization": f"Bearer {data['access_token']}",
    }

    response = await client.get(url, headers=headers)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_get_me_forbidden(
    client: AsyncClient,
    fastapi_app: FastAPI,
    mocked_verify_password: MockerFixture,
    create_user: User,
    create_role: Role,
    create_refresh_token: str,
) -> None:
    """Tests get_me handler without auth header."""
    url = fastapi_app.url_path_for("get_me")
    response = await client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
