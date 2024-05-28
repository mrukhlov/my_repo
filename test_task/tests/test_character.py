import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from test_task.db.dao.character_dao import CharacterDAO
from test_task.db.models.models import Character, User


@pytest.mark.anyio
async def test_create_character(  # noqa: WPS218
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_user: User,
) -> None:
    """Tests character creation."""
    url = fastapi_app.url_path_for("create_character_model")
    character_data = {
        "name": "New Character",
        "user_id": create_user.id,
        "level": 1,
        "experience": 0,
    }

    response = await client.post(url, json=character_data)
    assert response.status_code == status.HTTP_200_OK

    dao = CharacterDAO()
    character_list = await dao.filter_characters(
        name="New Character",
        user_id=create_user.id,
    )
    assert len(character_list) == 1

    character = character_list[0]
    assert character.name == "New Character"
    assert character.user_id == create_user.id  # type: ignore
    assert character.level == 1
    assert character.experience == 0


@pytest.mark.anyio
async def test_get_character_by_id(  # noqa: WPS218
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_character: Character,
) -> None:
    """Tests character retrieval."""
    url = fastapi_app.url_path_for(
        "get_character_model",
        character_id=create_character.id,
    )
    response = await client.get(url)
    character_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert character_data["id"] == create_character.id
    assert character_data["name"] == create_character.name
    assert character_data["user_id"] == create_character.user_id  # type: ignore
    assert character_data["level"] == create_character.level
    assert character_data["experience"] == create_character.experience


@pytest.mark.anyio
async def test_edit_character(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_character: Character,
) -> None:
    """Tests character editing."""
    new_data = {
        "name": "Updated Character",
        "level": 2,
        "experience": 100,
        "user_id": create_character.id,
    }

    url = fastapi_app.url_path_for(
        "edit_character_model",
        character_id=create_character.id,
    )
    response = await client.put(url, json=new_data)

    assert response.status_code == status.HTTP_200_OK

    edited_character = await Character.filter(id=create_character.id).first()
    assert edited_character.name == "Updated Character"  # type: ignore
    assert edited_character.level == 2  # type: ignore
    assert edited_character.experience == 100  # type: ignore


@pytest.mark.anyio
async def test_delete_character(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_character: Character,
) -> None:
    """Tests character deletion."""
    url = fastapi_app.url_path_for(
        "delete_character_model",
        character_id=create_character.id,
    )
    response = await client.delete(url)

    assert response.status_code == status.HTTP_200_OK

    deleted_character = await Character.filter(id=create_character.id).first()
    assert deleted_character is None
