import datetime
from typing import Any, AsyncGenerator, Dict

import pytest
from passlib.context import CryptContext
from pytest_mock import MockerFixture

from test_task.db.models.models import (
    Character,
    CurrencyBalance,
    CurrencyType,
    Equipment,
    Inventory,
    Role,
    Transaction,
    User,
)
from test_task.services.auth.auth import create_access_token
from test_task.services.auth.auth import create_refresh_token as cft


@pytest.fixture()
def test_token_lifetime() -> int:
    """Generates token lifetime.

    :return: token lifetime.
    """
    dt = datetime.datetime.now() + datetime.timedelta(days=1)
    return int(dt.timestamp())


@pytest.fixture()
def jwt_payload(
    test_token_lifetime: int,
) -> Dict[str, Any]:
    """Generates jwt payload.

    :return: jwt payload.
    """
    return {
        "exp": test_token_lifetime,
        "email": "aaa@aaa.com",
        "username": "aaa",
        "user_id": 1,
    }


@pytest.fixture()
def jwt_token(
    create_user: User,
) -> str:
    """Generates jwt token.

    :return: jwt token.
    """
    data = {
        "email": str(create_user.email),
        "username": str(create_user.username),
        "user_id": int(create_user.id),
    }
    return create_access_token(data)  # type: ignore


@pytest.fixture
async def create_user(
    create_role: Role,
) -> AsyncGenerator[User, None]:
    """
    Create an user for testing purposes.

    :yield: user
    """
    user = await User.create(
        username="test_user",
        email="test_user@example.com",
        password_hash="hashed_password",
        role=create_role,
    )
    yield user
    await user.delete()


@pytest.fixture
async def create_character(create_user: User) -> AsyncGenerator[Character, None]:
    """
    Create an character for testing purposes.

    :yield: character
    """
    character = await Character.create(
        name="John Doe",
        user=create_user,
        level=1,
        experience=0,
    )
    yield character
    await character.delete()


@pytest.fixture
async def create_character_from(create_user: User) -> AsyncGenerator[Character, None]:
    """
    Create an character for testing purposes.

    :yield: character
    """
    character = await Character.create(
        name="John Doe",
        user=create_user,
        level=1,
        experience=0,
    )
    yield character
    await character.delete()


@pytest.fixture
async def create_character_to(create_user: User) -> AsyncGenerator[Character, None]:
    """
    Create an character for testing purposes.

    :yield: character
    """
    character = await Character.create(
        name="John Doe",
        user=create_user,
        level=1,
        experience=0,
    )
    yield character
    await character.delete()


@pytest.fixture
async def create_equipment(
    create_character: Character,
    create_currency_type: CurrencyType,
) -> AsyncGenerator[Equipment, None]:
    """
    Create an equioment item for testing purposes.

    :yield: equipment
    """
    equipment = await Equipment.create(
        name="Sword",
        type="weapon",
        character=create_character,
        power=10,
        slot="weapon",
        equipped=False,
        price=10.0,
        currency_type=create_currency_type,
    )
    yield equipment
    await equipment.delete()


@pytest.fixture
async def create_currency_type() -> AsyncGenerator[CurrencyType, None]:
    """
    Create an currency type for testing purposes.

    :yield: currency type
    """
    currency_type = await CurrencyType.create(
        name="Gold",
        description="In-game currency",
    )
    yield currency_type
    await currency_type.delete()


@pytest.fixture
async def create_inventory(
    create_character: Character,
) -> AsyncGenerator[Inventory, None]:
    """
    Create an inventory item for testing purposes.

    :yield: inventory
    """
    inventory = await Inventory.create(
        character=create_character,
        item_name="Test Item",
        item_type="potion",
        quantity=10,
    )
    yield inventory
    await inventory.delete()


@pytest.fixture
async def create_currency_balance(
    create_character: Character,
    create_currency_type: CurrencyType,
) -> AsyncGenerator[CurrencyBalance, None]:
    """
    Create a currency balance for testing purposes.

    :yield: currency balance
    """
    currency_balance = await CurrencyBalance.create(
        character_id=create_character.id,
        currency_type_id=create_currency_type.id,
        balance=1000,
    )
    yield currency_balance
    await currency_balance.delete()


@pytest.fixture
async def create_transaction(
    create_character: Character,
    create_currency_type: CurrencyType,
) -> AsyncGenerator[Transaction, None]:
    """
    Create a transaction for testing purposes.

    :yield: transaction
    """
    transaction = await Transaction.create(
        transaction_type="in",
        amount=1000,
        currency_type_id=create_currency_type.id,
        character_to_id=create_character.id,
    )
    yield transaction
    await transaction.delete()


@pytest.fixture
async def create_refresh_token(create_user: User) -> str:
    """
    Create a refresh token.

    :return: refresh_token
    """
    data = {
        "email": create_user.email,
        "username": create_user.username,
        "user_id": create_user.id,
    }
    return cft(data)  # type: ignore


@pytest.fixture
async def create_role() -> AsyncGenerator[Role, None]:
    """
    Create an role for testing purposes.

    :yield: role
    """
    role = await Role.create(
        name="test_user",
        permissions={},
    )
    yield role
    await role.delete()


@pytest.fixture()
def mocked_verify_password(mocker: MockerFixture) -> MockerFixture:
    """
    Patch verify_password method.

    :param mocker: mocker.
    :return: mock.
    """
    mock = mocker.patch.object(CryptContext, "verify")
    mock.return_value = True
    return mock
