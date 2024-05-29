from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.exceptions import ValidationError
from tortoise.transactions import in_transaction

from test_task.db.dao.equipment_dao import EquipmentDAO
from test_task.db.models.models import (
    Character,
    CurrencyBalance,
    Equipment,
    Transaction,
)
from test_task.web.api.equipment.schema import (
    EquipmentModelDTO,
    EquipmentModelInputDTO,
    TransferEquipmentInputDTO,
)

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
            price=new_equipment_object.price,
            currency_type_id=new_equipment_object.currency_type_id,
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
        price=new_equipment_object.price,
        currency_type_id=new_equipment_object.currency_type_id,
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


@router.post("/transfer_item/")
async def transfer_item(
    transfer_object: TransferEquipmentInputDTO,
    equipment_dao: EquipmentDAO = Depends(),
) -> None:
    """
    Transfers equipment item from one character to another.

    :param transfer_object: data for transfer.
    :param equipment_dao: DAO for equipment models.
    :raises HTTPException: HTTPException
    """
    async with in_transaction() as connection:
        item_from = await equipment_dao.filter_equipment(
            equipment_id=transfer_object.item_id,
            character_id=transfer_object.character_from,
        )
        item_to = await equipment_dao.filter_equipment(
            equipment_id=transfer_object.item_id,
            character_id=transfer_object.character_to,
        )

        if not item_from or item_from[0].quantity == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str("Character doesn't have this item."),
            )

        character_to = await Character.filter(
            id=transfer_object.character_to,
        ).first()
        if not character_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str("Character doesn't exist."),
            )

        item_from_obj = item_from[0]
        await item_from_obj.fetch_related("currency_type", "character")

        balance_from, _ = await CurrencyBalance.get_or_create(
            character_id=transfer_object.character_from,
            currency_type_id=item_from_obj.currency_type.id,
        )

        if balance_from.balance < item_from_obj.price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str("Insufficient amount to transfer item."),
            )
        balance_from.balance -= item_from_obj.price * 0.85
        await balance_from.save(using_db=connection)

        item_from_obj.quantity -= 1
        await item_from_obj.save(using_db=connection)

        balance_from.balance -= float(item_from_obj.price)
        if item_to:
            item_to_obj = item_to[0]
            item_to_obj.quantity += 1
            await item_to_obj.save(using_db=connection)
        else:
            item_to_obj = await equipment_dao.create_equipment(
                name=item_from_obj.name,
                eq_type=item_from_obj.type,
                character_id=character_to.id,  # type: ignore
                power=item_from_obj.power,
                eq_slot=item_from_obj.slot.value,
                equipped=item_from_obj.equipped,
                price=item_from_obj.price,
                currency_type_id=item_from_obj.currency_type.id,
                quantity=1,
            )

        await Transaction.create(
            transaction_type="out",
            amount=item_from_obj.price * 0.85,
            item_id=item_from_obj.id,
            currency_type_id=item_from_obj.currency_type.id,
            character_from_id=transfer_object.character_from,
            character_to_id=transfer_object.character_to,
        )


@router.post("/drop_item/")
async def drop_item(
    drop_object: EquipmentModelInputDTO,
    equipment_dao: EquipmentDAO = Depends(),
) -> EquipmentModelDTO:
    """
    Transfers equipment item from one character to another.

    :param drop_object: data for transfer.
    :param equipment_dao: DAO for equipment models.
    :return: equipment object from database.
    """
    item_to = await equipment_dao.filter_equipment(
        name=drop_object.name,
        character_id=drop_object.character_id,
    )

    if item_to:
        item_to_object = item_to[0]
        item_to_object.quantity += 1
        await item_to_object.save()
    else:
        item_to_object = await equipment_dao.create_equipment(
            name=drop_object.name,
            eq_type=drop_object.type,
            character_id=drop_object.character_id,
            power=drop_object.power,
            eq_slot=drop_object.slot,
            equipped=drop_object.equipped,
            price=drop_object.price,
            currency_type_id=drop_object.currency_type_id,
        )

    return EquipmentModelDTO.model_validate(item_to_object)
