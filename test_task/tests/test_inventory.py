import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from test_task.db.dao.inventory_dao import InventoryDAO
from test_task.db.models.models import Character, Inventory


@pytest.mark.anyio
async def test_create_inventory(  # noqa: WPS218
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_character: Character,
) -> None:
    """Tests inventory creation."""
    url = fastapi_app.url_path_for("create_inventory_model")
    inventory_data = {
        "character_id": create_character.id,
        "item_name": "Potion of Healing",
        "item_type": "potion",
        "quantity": 5,
    }

    response = await client.post(url, json=inventory_data)
    assert response.status_code == status.HTTP_200_OK

    dao = InventoryDAO()
    inventories = await dao.filter_inventory(character_id=create_character.id)
    assert len(inventories) == 1

    inventory = inventories[0]
    await inventory.fetch_related(
        "character",
    )
    assert inventory.character.id == create_character.id
    assert inventory.item_name == "Potion of Healing"
    assert inventory.item_type == "potion"
    assert inventory.quantity == 5


@pytest.mark.anyio
async def test_get_inventory_by_id(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_inventory: Inventory,
) -> None:
    """Tests inventory retrieval."""
    url = fastapi_app.url_path_for(
        "get_inventory_model",
        inventory_id=create_inventory.id,
    )
    response = await client.get(url)
    inventory = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert inventory["item_name"] == create_inventory.item_name
    assert inventory["item_type"] == create_inventory.item_type
    assert inventory["quantity"] == create_inventory.quantity


@pytest.mark.anyio
async def test_edit_inventory(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_character: Character,
    create_inventory: Inventory,
) -> None:
    """Tests inventory editing."""
    new_data = {
        "character_id": create_character.id,
        "item_name": "Scroll of Fireball",
        "item_type": "scroll",
        "quantity": 10,
    }

    url = fastapi_app.url_path_for(
        "edit_inventory_model",
        inventory_id=create_inventory.id,
    )
    response = await client.put(url, json=new_data)

    assert response.status_code == status.HTTP_200_OK

    edited_inventory = await Inventory.filter(id=create_inventory.id).first()
    assert edited_inventory.item_name == "Scroll of Fireball"  # type: ignore
    assert edited_inventory.item_type == "scroll"  # type: ignore
    assert edited_inventory.quantity == 10  # type: ignore


@pytest.mark.anyio
async def test_delete_inventory(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_inventory: Inventory,
) -> None:
    """Tests inventory deletion."""
    url = fastapi_app.url_path_for(
        "delete_inventory_model",
        inventory_id=create_inventory.id,
    )
    response = await client.delete(url)

    assert response.status_code == status.HTTP_200_OK

    deleted_inventory = await Inventory.filter(id=create_inventory.id).first()
    assert deleted_inventory is None
