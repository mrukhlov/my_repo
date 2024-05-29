import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from test_task.db.dao.equipment_dao import EquipmentDAO
from test_task.db.models.models import Character, Equipment


@pytest.mark.anyio
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
        "slot": "weapon",
        "equipped": False,
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
    assert equipment.slot.value == "weapon"
    assert not equipment.equipped


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
    assert equipment["slot"] == create_equipment.slot.value
    assert equipment["equipped"] == create_equipment.equipped


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
        "slot": "chest",
        "equipped": False,
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
    assert edited_equipment.slot.value == "chest"  # type: ignore
    assert not edited_equipment.equipped  # type: ignore


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


@pytest.mark.anyio
async def test_equip_equipment(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_character: Character,
    create_equipment: Equipment,
) -> None:
    """Tests equipping an item."""
    new_data = {
        "name": create_equipment.name,
        "type": create_equipment.type,
        "character_id": create_character.id,
        "power": create_equipment.power,
        "slot": create_equipment.slot.value,
        "equipped": True,
    }

    url = fastapi_app.url_path_for(
        "edit_equipment_model",
        equipment_id=create_equipment.id,
    )
    response = await client.put(url, json=new_data)

    assert response.status_code == status.HTTP_200_OK

    equipped_equipment = await Equipment.filter(id=create_equipment.id).first()
    assert equipped_equipment.equipped  # type: ignore


@pytest.mark.anyio
async def test_create_equip_multiple_same_slot(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_character: Character,
    create_equipment: Equipment,
) -> None:
    """Tests equipping multiple items of the same slot fails."""
    new_data = {
        "name": create_equipment.name,
        "type": create_equipment.type,
        "character_id": create_character.id,
        "power": create_equipment.power,
        "slot": create_equipment.slot.value,
        "equipped": True,
    }

    url = fastapi_app.url_path_for(
        "edit_equipment_model",
        equipment_id=create_equipment.id,
    )
    response = await client.put(url, json=new_data)
    assert response.status_code == status.HTTP_200_OK

    equipment_data = {
        "name": "Sword of Might",
        "type": "weapon",
        "character_id": create_character.id,
        "power": 200,
        "slot": create_equipment.slot.value,
        "equipped": True,
    }

    url = fastapi_app.url_path_for("create_equipment_model")
    response = await client.post(url, json=equipment_data)
    assert response.status_code == status.HTTP_200_OK

    dao = EquipmentDAO()
    equipment_list = await dao.filter_equipment(character_id=create_character.id)
    assert len(equipment_list) == 2

    equipment = equipment_list[0]
    await equipment.fetch_related("character")
    assert equipment.name == create_equipment.name
    assert equipment.equipped

    equipment = equipment_list[1]
    await equipment.fetch_related("character")
    assert equipment.name == "Sword of Might"
    assert not equipment.equipped


@pytest.mark.anyio
async def test_equip_multiple_same_slot(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_character: Character,
    create_equipment: Equipment,
) -> None:
    """Tests equipping multiple items of the same slot fails."""
    new_data = {
        "name": create_equipment.name,
        "type": create_equipment.type,
        "character_id": create_character.id,
        "power": create_equipment.power,
        "slot": create_equipment.slot.value,
        "equipped": True,
    }

    url = fastapi_app.url_path_for(
        "edit_equipment_model",
        equipment_id=create_equipment.id,
    )
    edit_response = await client.put(url, json=new_data)
    assert edit_response.status_code == status.HTTP_200_OK

    equipment_data = {
        "name": "Sword of Might",
        "type": "weapon",
        "character_id": create_character.id,
        "power": 200,
        "slot": create_equipment.slot.value,
        "equipped": True,
    }

    url = fastapi_app.url_path_for("create_equipment_model")
    create_response = await client.post(url, json=equipment_data)
    assert create_response.status_code == status.HTTP_200_OK
    assert not create_response.json()["equipped"]

    equipment_data = {
        "name": "Sword of Might",
        "type": "weapon",
        "character_id": create_character.id,
        "power": 200,
        "slot": create_equipment.slot.value,
        "equipped": True,
    }

    url = fastapi_app.url_path_for(
        "edit_equipment_model",
        equipment_id=create_response.json()["id"],
    )
    equip_response = await client.put(url, json=equipment_data)
    assert equip_response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Character already has an equipped" in equip_response.json()["detail"]

    dao = EquipmentDAO()
    equipment_list = await dao.filter_equipment(character_id=create_character.id)
    assert len(equipment_list) == 2

    equipment = equipment_list[0]
    await equipment.fetch_related("character")
    assert equipment.name == create_equipment.name
