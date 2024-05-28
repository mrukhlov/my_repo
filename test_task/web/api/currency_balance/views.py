from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends

from test_task.db.dao.currency_balance_dao import CurrencyBalanceDAO
from test_task.db.models.models import CurrencyBalance
from test_task.web.api.currency_balance.schema import (
    CurrencyBalanceModelDTO,
    CurrencyBalanceModelInputDTO,
)

router = APIRouter()


@router.get("/", response_model=List[CurrencyBalanceModelDTO])
async def get_currency_balance_models(
    limit: int = 10,
    offset: int = 0,
    currency_balance_dao: CurrencyBalanceDAO = Depends(),
) -> List[CurrencyBalance]:
    """
    Retrieve all currency_balance objects from the database.

    :param limit: limit of currency_balance objects, defaults to 10.
    :param offset: offset of currency_balance objects, defaults to 0.
    :param currency_balance_dao: DAO for currency_balance models.
    :return: list of currency_balance objects from database.
    """
    return await currency_balance_dao.get_all_currency_balances(
        limit=limit,
        offset=offset,
    )


@router.get("/{currency_balance_id}/", response_model=CurrencyBalanceModelDTO)
async def get_currency_balance_model(
    currency_balance_id: int,
    currency_balance_dao: CurrencyBalanceDAO = Depends(),
) -> CurrencyBalanceModelDTO:
    """
    Retrieve currency_balance object from the database.

    :param currency_balance_id: currency_balance_id.
    :param currency_balance_dao: DAO for currency_balance models.
    :return: currency_balance object from database.
    """
    currency_balance = await currency_balance_dao.get_currency_balance_by_id(
        balance_id=currency_balance_id,
    )
    return CurrencyBalanceModelDTO.model_validate(currency_balance)


@router.put("/{currency_balance_id}/")
async def edit_currency_balance_model(
    currency_balance_id: int,
    new_currency_balance_object: CurrencyBalanceModelInputDTO,
    currency_balance_dao: CurrencyBalanceDAO = Depends(),
) -> None:
    """
    Edits currency_balance model in the database.

    :param currency_balance_id: currency_balance_id.
    :param new_currency_balance_object: new currency_balance model item.
    :param currency_balance_dao: DAO for currency_balance models.
    """
    await currency_balance_dao.edit_currency_balance(
        balance_id=currency_balance_id,
        balance=new_currency_balance_object.amount,
        character_id=new_currency_balance_object.character_id,
        currency_type_id=new_currency_balance_object.currency_type_id,
    )


@router.post("/")
async def create_currency_balance_model(
    new_currency_balance_object: CurrencyBalanceModelInputDTO,
    currency_balance_dao: CurrencyBalanceDAO = Depends(),
) -> None:
    """
    Creates currency_balance model in the database.

    :param new_currency_balance_object: new currency_balance model item.
    :param currency_balance_dao: DAO for currency_balance models.
    """
    await currency_balance_dao.create_currency_balance(
        character_id=new_currency_balance_object.character_id,
        currency_type_id=new_currency_balance_object.currency_type_id,
        balance=new_currency_balance_object.amount,
    )


@router.delete("/{currency_balance_id}/")
async def delete_currency_balance_model(
    currency_balance_id: int,
    currency_balance_dao: CurrencyBalanceDAO = Depends(),
) -> None:
    """
    Deletes currency_balance model in the database.

    :param currency_balance_id: currency_balance id.
    :param currency_balance_dao: DAO for currency_balance models.
    """
    currency_balance = await currency_balance_dao.get_currency_balance_by_id(
        currency_balance_id,
    )
    if currency_balance:
        await currency_balance.delete()
