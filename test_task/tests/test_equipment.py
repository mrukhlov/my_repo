import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from test_task.db.dao.equipment_dao import EquipmentDAO
from test_task.db.models.models import Character, Equipment


@pytest.mark.anyio
async def test_create_equipment(  # noqa: WPS218
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_character: Character,
) -> None:
    """Tests equipment creation."""
    url = fastapi_app.url_path_for("create_equipment_model")
    equipment_data = {
        "name": "Sword of Power",
        "type": "weapon",
        "character_id": create_character.id,
        "power": 100,
    }

    response = await client.post(url, json=equipment_data)
    assert response.status_code == status.HTTP_200_OK

    dao = EquipmentDAO()
    equipment_list = await dao.filter_equipment(character_id=create_character.id)
    assert len(equipment_list) == 1

    equipment = equipment_list[0]
    await equipment.fetch_related(
        "character",
    )

    assert equipment.name == "Sword of Power"
    assert equipment.type == "weapon"
    assert equipment.character.id == create_character.id
    assert equipment.power == 100


@pytest.mark.anyio
async def test_get_equipment_by_id(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_equipment: Equipment,
) -> None:
    """Tests equipment retrieval."""
    url = fastapi_app.url_path_for(
        "get_equipment_model",
        equipment_id=create_equipment.id,
    )
    response = await client.get(url)
    equipment = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert equipment["name"] == create_equipment.name
    assert equipment["type"] == create_equipment.type
    assert equipment["power"] == create_equipment.power
    assert equipment["character_id"] == create_equipment.character.id


@pytest.mark.anyio
async def test_edit_equipment(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_character: Character,
    create_equipment: Equipment,
) -> None:
    """Tests equipment editing."""
    new_data = {
        "name": "Shield of Invincibility",
        "type": "armor",
        "character_id": create_character.id,
        "power": 150,
    }

    url = fastapi_app.url_path_for(
        "edit_equipment_model",
        equipment_id=create_equipment.id,
    )
    response = await client.put(url, json=new_data)

    assert response.status_code == status.HTTP_200_OK

    edited_equipment = await Equipment.filter(id=create_equipment.id).first()
    assert edited_equipment.name == "Shield of Invincibility"  # type: ignore
    assert edited_equipment.type == "armor"  # type: ignore
    assert edited_equipment.power == 150  # type: ignore


@pytest.mark.anyio
async def test_delete_equipment(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_equipment: Equipment,
) -> None:
    """Tests equipment deletion."""
    url = fastapi_app.url_path_for(
        "delete_equipment_model",
        equipment_id=create_equipment.id,
    )
    response = await client.delete(url)

    assert response.status_code == status.HTTP_200_OK

    deleted_equipment = await Equipment.filter(id=create_equipment.id).first()
    assert deleted_equipment is None
