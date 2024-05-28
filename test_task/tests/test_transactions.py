import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from test_task.db.dao.transaction_dao import TransactionDAO
from test_task.db.models.models import Character, CurrencyType, Equipment


@pytest.mark.anyio
async def test_create_transaction(  # noqa: WPS218
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_equipment: Equipment,
    create_currency_type: CurrencyType,
    create_character: Character,
) -> None:
    """Tests transaction creation."""
    url = fastapi_app.url_path_for("create_transaction_model")
    transaction_data = {
        "transaction_type": "purchase",
        "amount": 100,
        "item_id": create_equipment.id,
        "currency_type_id": create_currency_type.id,
        "character_from_id": create_character.id,
        "character_to_id": create_character.id,
    }

    response = await client.post(url, json=transaction_data)
    assert response.status_code == status.HTTP_200_OK

    dao = TransactionDAO()
    transactions = await dao.filter_transactions(
        transaction_type="purchase",
        character_from_id=create_character.id,
        character_to_id=create_character.id,
    )
    assert len(transactions) == 1

    transaction = transactions[0]
    await transaction.fetch_related(
        "item",
        "currency_type",
        "character_from",
        "character_to",
    )

    assert transaction.amount == 100
    assert transaction.item.id == create_equipment.id
    assert transaction.currency_type.id == create_currency_type.id
    assert transaction.character_from.id == create_character.id
    assert transaction.character_to.id == create_character.id


@pytest.mark.anyio
async def test_get_transaction_by_id(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_equipment: Equipment,
    create_currency_type: CurrencyType,
    create_character_from: Character,
    create_character_to: Character,
) -> None:
    """Tests transaction retrieval."""
    dao = TransactionDAO()
    await dao.create_transaction(
        transaction_type="sale",
        amount=150,
        item_id=create_equipment.id,
        currency_type_id=create_currency_type.id,
        character_from_id=create_character_from.id,
        character_to_id=create_character_to.id,
    )

    url = fastapi_app.url_path_for("get_transaction_model", transaction_id=1)
    response = await client.get(url)
    transaction = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert transaction["amount"] == 150
    assert transaction["item"]["id"] == create_equipment.id
    assert transaction["currency_type"]["id"] == create_currency_type.id


@pytest.mark.anyio
async def test_edit_transaction(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_equipment: Equipment,
    create_currency_type: CurrencyType,
    create_character_from: Character,
    create_character_to: Character,
) -> None:
    """Tests transaction editing."""
    dao = TransactionDAO()
    created_transaction = await dao.create_transaction(
        transaction_type="purchase",
        amount=100,
        item_id=create_equipment.id,
        currency_type_id=create_currency_type.id,
        character_from_id=create_character_from.id,
        character_to_id=create_character_to.id,
    )

    new_data = {
        "transaction_type": "sale",
        "amount": 200,
        "item_id": create_equipment.id,
        "currency_type_id": create_currency_type.id,
        "character_from_id": create_character_from.id,
        "character_to_id": create_character_to.id,
    }

    url = fastapi_app.url_path_for(
        "edit_transaction_model",
        transaction_id=created_transaction.id,
    )
    response = await client.put(url, json=new_data)

    assert response.status_code == status.HTTP_200_OK

    edited_transaction = await dao.get_transaction_by_id(
        created_transaction.id,
    )
    assert edited_transaction.transaction_type == "sale"  # type: ignore
    assert edited_transaction.amount == 200  # type: ignore


@pytest.mark.anyio
async def test_delete_transaction(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_equipment: Equipment,
    create_currency_type: CurrencyType,
    create_character: Character,
) -> None:
    """Tests transaction deletion."""
    dao = TransactionDAO()
    created_transaction = await dao.create_transaction(
        transaction_type="purchase",
        amount=100,
        item_id=create_equipment.id,
        currency_type_id=create_currency_type.id,
        character_from_id=create_character.id,
        character_to_id=create_character.id,
    )

    url = fastapi_app.url_path_for(
        "delete_transaction_model",
        transaction_id=created_transaction.id,
    )
    response = await client.delete(url)

    assert response.status_code == status.HTTP_200_OK

    deleted_transaction = await dao.get_transaction_by_id(created_transaction.id)
    assert deleted_transaction is None
