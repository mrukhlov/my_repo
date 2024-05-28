from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends

from test_task.db.dao.transaction_dao import TransactionDAO
from test_task.db.models.models import Transaction
from test_task.web.api.transaction.schema import (
    TransactionModelDTO,
    TransactionModelInputDTO,
)

router = APIRouter()


@router.get("/", response_model=List[TransactionModelDTO])
async def get_transaction_models(
    limit: int = 10,
    offset: int = 0,
    transaction_dao: TransactionDAO = Depends(),
) -> List[Transaction]:
    """
    Retrieve all transaction objects from the database.

    :param limit: limit of transaction objects, defaults to 10.
    :param offset: offset of transaction objects, defaults to 0.
    :param transaction_dao: DAO for transaction models.
    :return: list of transaction objects from database.
    """
    return await transaction_dao.get_all_transactions(limit=limit, offset=offset)


@router.get("/{transaction_id}/", response_model=TransactionModelDTO)
async def get_transaction_model(
    transaction_id: int,
    transaction_dao: TransactionDAO = Depends(),
) -> TransactionModelDTO:
    """
    Retrieve transaction object from the database.

    :param transaction_id: transaction id.
    :param transaction_dao: DAO for transaction models.
    :return: list of transaction objects from database.
    """
    transaction = await transaction_dao.get_transaction_by_id(
        transaction_id=transaction_id,
    )
    return TransactionModelDTO.model_validate(transaction)


@router.put("/{transaction_id}/")
async def edit_transaction_model(
    transaction_id: int,
    new_transaction_object: TransactionModelInputDTO,
    transaction_dao: TransactionDAO = Depends(),
) -> None:
    """
    Creates transaction model in the database.

    :param transaction_id: transaction id.
    :param new_transaction_object: new transaction model item.
    :param transaction_dao: DAO for transaction models.
    """
    await transaction_dao.edit_transaction(
        transaction_id=transaction_id,
        transaction_type=new_transaction_object.transaction_type,
        amount=new_transaction_object.amount,
        item_id=new_transaction_object.item_id,
        currency_type_id=new_transaction_object.currency_type_id,
        character_from_id=new_transaction_object.character_from_id,
        character_to_id=new_transaction_object.character_to_id,
    )


@router.post("/")
async def create_transaction_model(
    new_transaction_object: TransactionModelInputDTO,
    transaction_dao: TransactionDAO = Depends(),
) -> TransactionModelDTO:
    """
    Creates transaction model in the database.

    :param new_transaction_object: new transaction model item.
    :param transaction_dao: DAO for transaction models.
    :return: inventory object from database.
    """
    transaction = await transaction_dao.create_transaction(
        transaction_type=new_transaction_object.transaction_type,
        amount=new_transaction_object.amount,
        item_id=new_transaction_object.item_id,
        currency_type_id=new_transaction_object.currency_type_id,
        character_from_id=new_transaction_object.character_from_id,
        character_to_id=new_transaction_object.character_to_id,
    )
    return TransactionModelDTO.model_validate(transaction)


@router.delete("/{transaction_id}/")
async def delete_transaction_model(
    transaction_id: int,
    transaction_dao: TransactionDAO = Depends(),
) -> None:
    """
    Deletes transaction model in the database.

    :param transaction_id: transaction id.
    :param transaction_dao: DAO for transaction models.
    """
    transaction = await transaction_dao.get_transaction_by_id(transaction_id)
    if transaction:
        await transaction.delete()
