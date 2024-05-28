import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from test_task.db.dao.user_dao import UserDAO


@pytest.mark.anyio
async def test_creation(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests user instance creation."""
    url = fastapi_app.url_path_for("create_user_model")
    test_name = uuid.uuid4().hex
    response = await client.post(
        url,
        json={
            "username": test_name,
            "email": "test_email",
            "password_hash": "test_password_hash",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    dao = UserDAO()
    instances = await dao.filter_users(username=test_name)
    assert instances[0].username == test_name


@pytest.mark.anyio
async def test_getting(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests user instance retrieval."""
    dao = UserDAO()
    test_name = uuid.uuid4().hex
    await dao.create_user(
        username=test_name,
        email="email",
        password_hash="password_hash",
    )
    url = fastapi_app.url_path_for("get_user_models")
    response = await client.get(url)
    dummies = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(dummies) == 1
    assert dummies[0]["username"] == test_name


@pytest.mark.anyio
async def test_edit_user_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests user model editing."""
    user_dao = UserDAO()
    test_username = uuid.uuid4().hex
    test_email = f"{test_username}@example.com"
    test_password_hash = uuid.uuid4().hex
    created_user = await user_dao.create_user(
        username=test_username,
        email=test_email,
        password_hash=test_password_hash,
    )

    new_username = uuid.uuid4().hex
    new_email = f"{new_username}@example.com"
    new_password_hash = uuid.uuid4().hex
    url = fastapi_app.url_path_for("edit_user_model", user_id=created_user.id)
    response = await client.put(
        url,
        json={
            "username": new_username,
            "email": new_email,
            "password_hash": new_password_hash,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    edited_user = await user_dao.get_user_by_id(created_user.id)
    assert edited_user.username == new_username  # type: ignore
    assert edited_user.email == new_email  # type: ignore
    assert edited_user.password_hash == new_password_hash  # type: ignore


@pytest.mark.anyio
async def test_delete_user_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests user model deletion."""
    user_dao = UserDAO()
    test_username = uuid.uuid4().hex
    test_email = f"{test_username}@example.com"
    test_password_hash = uuid.uuid4().hex
    created_user = await user_dao.create_user(
        username=test_username,
        email=test_email,
        password_hash=test_password_hash,
    )

    url = fastapi_app.url_path_for("delete_user_model", user_id=created_user.id)
    response = await client.delete(url)

    assert response.status_code == status.HTTP_200_OK

    deleted_user = await user_dao.get_user_by_id(created_user.id)
    assert deleted_user is None
