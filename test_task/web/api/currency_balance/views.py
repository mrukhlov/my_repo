from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from tortoise.expressions import Q  # noqa: WPS347

from test_task.db.dao.currency_balance_dao import CurrencyBalanceDAO
from test_task.db.models.models import Character, CurrencyBalance, Transaction
from test_task.web.api.currency_balance.schema import (
    CurrencyBalanceModelDTO,
    CurrencyBalanceModelInputDTO,
)
from test_task.web.api.transaction.schema import TransactionModelDTO
from test_task.web.utils import send_email

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
        balance=new_currency_balance_object.amount,  # type: ignore
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


@router.post("/top_up_currency_balance/")
async def top_up_currency_balance(
    top_up_object: CurrencyBalanceModelInputDTO,
    background_tasks: BackgroundTasks,
    currency_balance_dao: CurrencyBalanceDAO = Depends(),
) -> CurrencyBalanceModelDTO:
    """
    Top up currency balance of the character.

    :param top_up_object: data for transfer.
    :param background_tasks: background_tasks.
    :param currency_balance_dao: DAO for currency_balance models.
    :return: currency_balance object from database.
    """
    currency_balance = await currency_balance_dao.filter_currency_balances(
        character_id=top_up_object.character_id,
        currency_type=top_up_object.currency_type_id,
    )

    if currency_balance:
        currency_balance_object = currency_balance[0]
        currency_balance_object.balance += top_up_object.amount
        await currency_balance_object.save()
    else:
        currency_balance_object = await currency_balance_dao.create_currency_balance(
            character_id=top_up_object.character_id,
            currency_type_id=top_up_object.currency_type_id,
            balance=top_up_object.amount,
        )

    await Transaction.create(
        transaction_type="in",
        amount=top_up_object.amount,
        currency_type_id=top_up_object.currency_type_id,
        character_to_id=top_up_object.character_id,
    )

    character = (
        await Character.filter(id=top_up_object.character_id)
        .prefetch_related("user")
        .first()
    )

    background_tasks.add_task(
        send_email,
        character.user.email,  # type: ignore
        f"Hello {character.user.username} top up balance successful.",  # type: ignore # noqa: WPS237, E501
        f"Your balance increased by {top_up_object.amount}, enjoy!",
    )

    return CurrencyBalanceModelDTO.model_validate(currency_balance_object)


@router.get(
    "/check_balance_history/{currency_balance_id}/{currency_type_id}/",
    response_model=List[TransactionModelDTO],
)
async def check_balance_history(
    currency_balance_id: int,
    currency_type_id: int,
    currency_balance_dao: CurrencyBalanceDAO = Depends(),
) -> List[Transaction]:
    """
    Retrieve currency balance transactions history from the database.

    :param currency_balance_id: currency_balance_id.
    :param currency_type_id: currency_type_id.
    :param currency_balance_dao: DAO for currency_balance models.
    :raises HTTPException: HTTPException
    :return: transaction object from database.
    """
    currency_balance = await currency_balance_dao.filter_currency_balances(
        currency_balance_id=currency_balance_id,
        currency_type=currency_type_id,
    )
    if not currency_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str("Balance does not exist."),
        )

    currency_balance_obj = currency_balance[0]
    await currency_balance_obj.fetch_related("character")

    return await Transaction.filter(
        (
            Q(
                character_from_id=currency_balance_obj.character.id,
            )
            | Q(
                character_to_id=currency_balance_obj.character.id,
            )
        ),
    ).prefetch_related(
        "character_from",
        "character_to",
        "item",
        "currency_type",
    )
