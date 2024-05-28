import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from test_task.db.dao.currency_type_dao import CurrencyTypeDAO
from test_task.db.models.models import CurrencyType


@pytest.mark.anyio
async def test_create_currency_type(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests currency type creation."""
    url = fastapi_app.url_path_for("create_currency_type_model")
    currency_type_data = {
        "name": "Gold",
        "description": "Standard currency",
    }

    response = await client.post(url, json=currency_type_data)
    assert response.status_code == status.HTTP_200_OK

    dao = CurrencyTypeDAO()
    currency_type_list = await dao.filter_currency_types(name="Gold")
    assert len(currency_type_list) == 1

    currency_type = currency_type_list[0]
    assert currency_type.name == "Gold"
    assert currency_type.description == "Standard currency"


@pytest.mark.anyio
async def test_get_currency_type_by_id(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_currency_type: CurrencyType,
) -> None:
    """Tests currency type retrieval."""
    url = fastapi_app.url_path_for("get_currency_type_models")
    response = await client.get(url)
    currency_types = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert any(ct["id"] == create_currency_type.id for ct in currency_types)


@pytest.mark.anyio
async def test_edit_currency_type(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_currency_type: CurrencyType,
) -> None:
    """Tests currency type editing."""
    new_data = {
        "name": "Platinum",
        "description": "High value currency",
    }

    url = fastapi_app.url_path_for(
        "edit_currency_type_model",
        currency_type_id=create_currency_type.id,
    )
    response = await client.put(url, json=new_data)

    assert response.status_code == status.HTTP_200_OK

    edited_currency_type = await CurrencyType.filter(id=create_currency_type.id).first()
    assert edited_currency_type.name == "Platinum"  # type: ignore
    assert edited_currency_type.description == "High value currency"  # type: ignore


@pytest.mark.anyio
async def test_delete_currency_type(
    fastapi_app: FastAPI,
    client: AsyncClient,
    create_currency_type: CurrencyType,
) -> None:
    """Tests currency type deletion."""
    url = fastapi_app.url_path_for(
        "delete_currency_type_model",
        currency_type_id=create_currency_type.id,
    )
    response = await client.delete(url)

    assert response.status_code == status.HTTP_200_OK

    deleted_currency_type = await CurrencyType.filter(
        id=create_currency_type.id,
    ).first()
    assert deleted_currency_type is None
