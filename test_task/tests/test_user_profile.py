import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from test_task.db.dao.user_profile_dao import UserProfileDAO
from test_task.db.models.models import User


@pytest.mark.anyio
async def test_creation_user_profile(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_user: User,
) -> None:
    """Tests user profile instance creation."""
    url = fastapi_app.url_path_for("create_user_profile_model")
    test_bio = "Test Bio"
    response = await client.post(
        url,
        json={
            "user_id": create_user.id,
            "bio": test_bio,
            "avatar_url": "test_avatar_url",
            "location": "test_location",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    dao = UserProfileDAO()
    instances = await dao.filter_user_profiles(user_id=create_user.id)
    assert instances[0].bio == test_bio


@pytest.mark.anyio
async def test_getting_user_profiles(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_user: User,
) -> None:
    """Tests user profile instance retrieval."""
    dao = UserProfileDAO()
    test_bio = "Test Bio"
    await dao.create_user_profile(
        user_id=create_user.id,
        bio=test_bio,
        avatar_url="test_avatar_url",
        location="test_location",
    )
    url = fastapi_app.url_path_for("get_user_profile_models")
    response = await client.get(url)
    profiles = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(profiles) == 1
    assert profiles[0]["bio"] == test_bio


@pytest.mark.anyio
async def test_edit_user_profile_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_user: User,
) -> None:
    """Tests user profile model editing."""
    profile_dao = UserProfileDAO()
    test_bio = "Test Bio"
    test_location = "Test Location"
    created_profile = await profile_dao.create_user_profile(
        user_id=create_user.id,
        bio=test_bio,
        avatar_url="test_avatar_url",
        location=test_location,
    )

    new_bio = "New Bio"
    new_location = "New Location"
    url = fastapi_app.url_path_for(
        "edit_user_profile_model",
        user_profile_id=created_profile.id,
    )
    response = await client.put(
        url,
        json={
            "user_id": create_user.id,
            "bio": new_bio,
            "avatar_url": "new_avatar_url",
            "location": new_location,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    edited_profile = await profile_dao.get_user_profile_by_id(created_profile.id)
    assert edited_profile.bio == new_bio  # type: ignore
    assert edited_profile.location == new_location  # type: ignore


@pytest.mark.anyio
async def test_delete_user_profile_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_user: User,
) -> None:
    """Tests user profile model deletion."""
    profile_dao = UserProfileDAO()
    test_bio = "Test Bio"
    test_location = "Test Location"
    created_profile = await profile_dao.create_user_profile(
        user_id=create_user.id,
        bio=test_bio,
        avatar_url="test_avatar_url",
        location=test_location,
    )

    url = fastapi_app.url_path_for(
        "delete_user_profile_model",
        user_profile_id=created_profile.id,
    )
    response = await client.delete(url)

    assert response.status_code == status.HTTP_200_OK

    deleted_profile = await profile_dao.get_user_profile_by_id(created_profile.id)
    assert deleted_profile is None
