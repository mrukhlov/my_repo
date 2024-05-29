import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from test_task.db.dao.currency_balance_dao import CurrencyBalanceDAO
from test_task.db.models.models import Character, CurrencyBalance, CurrencyType


@pytest.mark.anyio
async def test_create_currency_balance(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_character: Character,
    create_currency_type: CurrencyType,
) -> None:
    """Tests currency balance creation."""
    url = fastapi_app.url_path_for("create_currency_balance_model")
    currency_balance_data = {
        "character_id": create_character.id,
        "currency_type_id": create_currency_type.id,
        "amount": 1000,
    }

    response = await client.post(url, json=currency_balance_data)
    assert response.status_code == status.HTTP_200_OK

    dao = CurrencyBalanceDAO()
    currency_balance_list = await dao.filter_currency_balances(
        character_id=create_character.id,
        currency_type=create_currency_type.id,  # type: ignore
    )
    assert len(currency_balance_list) == 1

    currency_balance = currency_balance_list[0]
    await currency_balance.fetch_related(
        "character",
        "currency_type",
    )

    assert currency_balance.character_id == create_character.id  # type: ignore
    assert currency_balance.currency_type_id == create_currency_type.id  # type: ignore
    assert currency_balance.balance == 1000


@pytest.mark.anyio
async def test_get_currency_balance_by_id(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_currency_balance: CurrencyBalance,
) -> None:
    """Tests currency balance retrieval."""
    url = fastapi_app.url_path_for(
        "get_currency_balance_model",
        currency_balance_id=create_currency_balance.id,
    )
    response = await client.get(url)
    currency_balance = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert currency_balance["id"] == create_currency_balance.id
    assert currency_balance["character_id"] == create_currency_balance.character_id  # type: ignore  # noqa: E501
    assert currency_balance["currency_type_id"] == create_currency_balance.currency_type_id  # type: ignore  # noqa: E501
    assert currency_balance["balance"] == create_currency_balance.balance


@pytest.mark.anyio
async def test_edit_currency_balance(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_currency_balance: CurrencyBalance,
    create_character: Character,
    create_currency_type: CurrencyType,
) -> None:
    """Tests currency balance editing."""
    new_data = {
        "amount": 2000,
        "character_id": create_character.id,
        "currency_type_id": create_currency_type.id,
    }

    url = fastapi_app.url_path_for(
        "edit_currency_balance_model",
        currency_balance_id=create_currency_balance.id,
    )
    response = await client.put(url, json=new_data)

    assert response.status_code == status.HTTP_200_OK

    edited_currency_balance = await CurrencyBalance.filter(
        id=create_currency_balance.id,
    ).first()
    assert edited_currency_balance.balance == 2000  # type: ignore


@pytest.mark.anyio
async def test_delete_currency_balance(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_currency_balance: CurrencyBalance,
) -> None:
    """Tests currency balance deletion."""
    url = fastapi_app.url_path_for(
        "delete_currency_balance_model",
        currency_balance_id=create_currency_balance.id,
    )
    response = await client.delete(url)

    assert response.status_code == status.HTTP_200_OK

    deleted_currency_balance = await CurrencyBalance.filter(
        id=create_currency_balance.id,
    ).first()
    assert deleted_currency_balance is None


@pytest.mark.anyio
async def test_top_up_currency_balance_existing_balance(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_character: Character,
    create_currency_type: CurrencyType,
    create_currency_balance: CurrencyBalance,
) -> None:
    """Tests topping up an existing currency balance."""
    url = fastapi_app.url_path_for("top_up_currency_balance")
    top_up_data = {
        "character_id": create_character.id,
        "currency_type_id": create_currency_type.id,
        "amount": 500,
    }

    response = await client.post(url, json=top_up_data)
    assert response.status_code == status.HTTP_200_OK

    dao = CurrencyBalanceDAO()
    currency_balance = await dao.filter_currency_balances(
        character_id=create_character.id,
        currency_type=create_currency_type.id,
    )

    assert currency_balance[0].balance == create_currency_balance.balance + 500


@pytest.mark.anyio
async def test_top_up_currency_balance_new_balance(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_character: Character,
    create_currency_type: CurrencyType,
) -> None:
    """Tests topping up a non-existing currency balance."""
    url = fastapi_app.url_path_for("top_up_currency_balance")
    top_up_data = {
        "character_id": create_character.id,
        "currency_type_id": create_currency_type.id,
        "amount": 1000,
    }

    response = await client.post(url, json=top_up_data)
    assert response.status_code == status.HTTP_200_OK

    dao = CurrencyBalanceDAO()
    currency_balance = await dao.filter_currency_balances(
        character_id=create_character.id,
        currency_type=create_currency_type.id,
    )

    assert currency_balance[0].balance == 1000
