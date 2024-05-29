from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.exceptions import ValidationError

from test_task.db.dao.equipment_dao import EquipmentDAO
from test_task.db.models.models import Equipment
from test_task.web.api.equipment.schema import EquipmentModelDTO, EquipmentModelInputDTO

router = APIRouter()


@router.get("/", response_model=List[EquipmentModelDTO])
async def get_equipment_models(
    limit: int = 10,
    offset: int = 0,
    equipment_dao: EquipmentDAO = Depends(),
) -> List[Equipment]:
    """
    Retrieve all equipment objects from the database.

    :param limit: limit of equipment objects, defaults to 10.
    :param offset: offset of equipment objects, defaults to 0.
    :param equipment_dao: DAO for equipment models.
    :return: list of equipment objects from database.
    """
    return await equipment_dao.get_all_equipment(limit=limit, offset=offset)


@router.get("/{equipment_id}/", response_model=EquipmentModelDTO)
async def get_equipment_model(
    equipment_id: int,
    equipment_dao: EquipmentDAO = Depends(),
) -> EquipmentModelDTO:
    """
    Retrieve equipment object from the database.

    :param equipment_id: equipment_id.
    :param equipment_dao: DAO for equipment models.
    :return: equipment object from database.
    """
    equipment = await equipment_dao.get_equipment_by_id(
        equipment_id=equipment_id,
    )
    return EquipmentModelDTO.model_validate(equipment)


@router.put("/{equipment_id}/")
async def edit_equipment_model(
    equipment_id: int,
    new_equipment_object: EquipmentModelInputDTO,
    equipment_dao: EquipmentDAO = Depends(),
) -> EquipmentModelDTO:
    """
    Edits equipment model in the database.

    :param equipment_id: equipment_id.
    :param new_equipment_object: new equipment model item.
    :param equipment_dao: DAO for equipment models.
    :raises HTTPException: HTTPException
    :return: equipment object from database.
    """
    try:
        equipment = await equipment_dao.edit_equipment(
            equipment_id=equipment_id,
            name=new_equipment_object.name,
            eq_type=new_equipment_object.type,
            character_id=new_equipment_object.character_id,
            power=new_equipment_object.power,
            eq_slot=new_equipment_object.slot,
            equipped=new_equipment_object.equipped,
        )
    except ValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )
    return EquipmentModelDTO.model_validate(equipment)


@router.post("/")
async def create_equipment_model(
    new_equipment_object: EquipmentModelInputDTO,
    equipment_dao: EquipmentDAO = Depends(),
) -> EquipmentModelDTO:
    """
    Creates equipment model in the database.

    :param new_equipment_object: new equipment model item.
    :param equipment_dao: DAO for equipment models.
    :return: equipment object from database.
    """
    equipment = await equipment_dao.create_equipment(
        name=new_equipment_object.name,
        eq_type=new_equipment_object.type,
        character_id=new_equipment_object.character_id,
        power=new_equipment_object.power,
        eq_slot=new_equipment_object.slot,
        equipped=new_equipment_object.equipped,
    )

    return EquipmentModelDTO.model_validate(equipment)


@router.delete("/{equipment_id}/")
async def delete_equipment_model(
    equipment_id: int,
    equipment_dao: EquipmentDAO = Depends(),
) -> None:
    """
    Deletes equipment model in the database.

    :param equipment_id: equipment id.
    :param equipment_dao: DAO for equipment models.
    """
    equipment = await equipment_dao.get_equipment_by_id(equipment_id)
    if equipment:
        await equipment.delete()
