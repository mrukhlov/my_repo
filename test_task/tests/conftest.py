from typing import AsyncGenerator

import pytest

from test_task.db.models.models import (
    Character,
    CurrencyBalance,
    CurrencyType,
    Equipment,
    Inventory,
    User,
)


@pytest.fixture
async def create_user() -> AsyncGenerator[User, None]:
    """
    Create an user for testing purposes.

    :yield: user
    """
    user = await User.create(
        username="test_user",
        email="test_user@example.com",
        password_hash="hashed_password",
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
