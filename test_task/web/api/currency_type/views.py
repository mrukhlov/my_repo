from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends

from test_task.db.dao.currency_type_dao import CurrencyTypeDAO
from test_task.db.models.models import CurrencyType
from test_task.web.api.currency_type.schema import (
    CurrencyTypeModelDTO,
    CurrencyTypeModelInputDTO,
)

router = APIRouter()


@router.get("/", response_model=List[CurrencyTypeModelDTO])
async def get_currency_type_models(
    limit: int = 10,
    offset: int = 0,
    currency_type_dao: CurrencyTypeDAO = Depends(),
) -> List[CurrencyType]:
    """
    Retrieve all currency_type objects from the database.

    :param limit: limit of currency_type objects, defaults to 10.
    :param offset: offset of currency_type objects, defaults to 0.
    :param currency_type_dao: DAO for currency_type models.
    :return: list of currency_type objects from database.
    """
    return await currency_type_dao.get_all_currency_types(limit=limit, offset=offset)


@router.get("/{currency_type_id}/", response_model=CurrencyTypeModelDTO)
async def get_currency_type_model(
    currency_type_id: int,
    currency_type_dao: CurrencyTypeDAO = Depends(),
) -> CurrencyTypeModelDTO:
    """
    Retrieve currency_type object from the database.

    :param currency_type_id: currency_type_id.
    :param currency_type_dao: DAO for currency_type models.
    :return: currency_type object from database.
    """
    currency_type = await currency_type_dao.get_currency_type_by_id(
        type_id=currency_type_id,
    )
    return CurrencyTypeModelDTO.model_validate(currency_type)


@router.put("/{currency_type_id}/")
async def edit_currency_type_model(
    currency_type_id: int,
    new_currency_type_object: CurrencyTypeModelInputDTO,
    currency_type_dao: CurrencyTypeDAO = Depends(),
) -> None:
    """
    Creates currency_type model in the database.

    :param currency_type_id: currency_type_id.
    :param new_currency_type_object: new currency_type model item.
    :param currency_type_dao: DAO for currency_type models.
    """
    await currency_type_dao.edit_currency_type(
        type_id=currency_type_id,
        name=new_currency_type_object.name,
        description=new_currency_type_object.description,
    )


@router.post("/")
async def create_currency_type_model(
    new_currency_type_object: CurrencyTypeModelInputDTO,
    currency_type_dao: CurrencyTypeDAO = Depends(),
) -> None:
    """
    Creates currency_type model in the database.

    :param new_currency_type_object: new currency_type model item.
    :param currency_type_dao: DAO for currency_type models.
    """
    await currency_type_dao.create_currency_type(
        name=new_currency_type_object.name,
        description=new_currency_type_object.description,
    )


@router.delete("/{currency_type_id}/")
async def delete_currency_type_model(
    currency_type_id: int,
    currency_type_dao: CurrencyTypeDAO = Depends(),
) -> None:
    """
    Deletes currency_type model in the database.

    :param currency_type_id: currency_type id.
    :param currency_type_dao: DAO for currency_type models.
    """
    currency_type = await currency_type_dao.get_currency_type_by_id(currency_type_id)
    if currency_type:
        await currency_type.delete()
