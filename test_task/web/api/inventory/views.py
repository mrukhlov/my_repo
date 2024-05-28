from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends

from test_task.db.dao.inventory_dao import InventoryDAO
from test_task.db.models.models import Inventory
from test_task.web.api.inventory.schema import InventoryModelDTO, InventoryModelInputDTO

router = APIRouter()


@router.get("/", response_model=List[InventoryModelDTO])
async def get_inventory_models(
    limit: int = 10,
    offset: int = 0,
    inventory_dao: InventoryDAO = Depends(),
) -> List[Inventory]:
    """
    Retrieve all inventory objects from the database.

    :param limit: limit of inventory objects, defaults to 10.
    :param offset: offset of inventory objects, defaults to 0.
    :param inventory_dao: DAO for inventory models.
    :return: list of inventory objects from database.
    """
    return await inventory_dao.get_all_inventory(limit=limit, offset=offset)


@router.get("/{inventory_id}/", response_model=InventoryModelDTO)
async def get_inventory_model(
    inventory_id: int,
    inventory_dao: InventoryDAO = Depends(),
) -> InventoryModelDTO:
    """
    Retrieve inventory object from the database.

    :param inventory_id: inventory id.
    :param inventory_dao: DAO for inventory models.
    :return: inventory object from database.
    """
    inventory = await inventory_dao.get_inventory_by_id(
        inventory_id=inventory_id,
    )
    return InventoryModelDTO.model_validate(inventory)


@router.put("/{inventory_id}/")
async def edit_inventory_model(
    inventory_id: int,
    new_inventory_object: InventoryModelInputDTO,
    inventory_dao: InventoryDAO = Depends(),
) -> None:
    """
    Edits inventory model in the database.

    :param inventory_id: inventory id.
    :param new_inventory_object: new inventory model item.
    :param inventory_dao: DAO for inventory models.
    """
    await inventory_dao.edit_inventory(
        inventory_id=inventory_id,
        character_id=new_inventory_object.character_id,
        item_name=new_inventory_object.item_name,
        item_type=new_inventory_object.item_type,
        quantity=new_inventory_object.quantity,
    )


@router.post("/")
async def create_inventory_model(
    new_inventory_object: InventoryModelInputDTO,
    inventory_dao: InventoryDAO = Depends(),
) -> InventoryModelDTO:
    """
    Creates inventory model in the database.

    :param new_inventory_object: new inventory model item.
    :param inventory_dao: DAO for inventory models.
    :return: inventory object from database.
    """
    inventory = await inventory_dao.create_inventory(
        character_id=new_inventory_object.character_id,
        item_name=new_inventory_object.item_name,
        item_type=new_inventory_object.item_type,
        quantity=new_inventory_object.quantity,
    )
    return InventoryModelDTO.model_validate(inventory)


@router.delete("/{inventory_id}/")
async def delete_inventory_model(
    inventory_id: int,
    inventory_dao: InventoryDAO = Depends(),
) -> None:
    """
    Deletes inventory model in the database.

    :param inventory_id: inventory id.
    :param inventory_dao: DAO for inventory models.
    """
    inventory = await inventory_dao.get_inventory_by_id(inventory_id)
    if inventory:
        await inventory.delete()
