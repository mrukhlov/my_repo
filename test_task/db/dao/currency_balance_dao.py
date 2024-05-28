from typing import List, Optional

from test_task.db.models.models import Character, CurrencyBalance, CurrencyType


class CurrencyBalanceDAO:
    """Class for accessing the currency balance table."""

    async def create_currency_balance(
        self,
        character_id: int,
        currency_type_id: int,
        balance: int = 0,
    ) -> None:
        """
        Add single currency balance to the database.

        :param character_id: ID of the character who owns the currency balance.
        :param currency_type_id: type of the currency (e.g., "gold", "gems").
        :param balance: balance of the currency.
        """
        await CurrencyBalance.create(
            character_id=character_id,
            currency_type_id=currency_type_id,
            balance=balance,
        )

    async def get_currency_balance_by_id(
        self,
        balance_id: int,
    ) -> Optional[CurrencyBalance]:
        """
        Get currency balance by ID.

        :param balance_id: ID of the currency balance.
        :return: currency balance instance or None.
        """
        return (
            await CurrencyBalance.filter(id=balance_id)
            .prefetch_related(
                "character",
                "currency_type",
            )
            .first()
        )

    async def get_all_currency_balances(
        self,
        limit: int,
        offset: int,
    ) -> List[CurrencyBalance]:
        """
        Get all currency balances with limit/offset pagination.

        :param limit: limit of currency balances.
        :param offset: offset of currency balances.
        :return: list of currency balances.
        """
        return await CurrencyBalance.all().offset(offset).limit(limit)

    async def filter_currency_balances(
        self,
        character_id: Optional[int] = None,
        currency_type: Optional[str] = None,
    ) -> List[CurrencyBalance]:
        """
        Get specific currency balance models.

        :param character_id: ID of character who owns the currency balance.
        :param currency_type: type of the currency.
        :return: currency balance models.
        """
        filters = {}
        if character_id:
            filters["character_id"] = character_id
        if currency_type:
            filters["currency_type"] = currency_type  # type: ignore
        return await CurrencyBalance.filter(**filters).all()

    async def edit_currency_balance(  # noqa: C901
        self,
        balance_id: int,
        balance: Optional[int] = None,
        character_id: Optional[int] = None,
        currency_type_id: Optional[int] = None,
    ) -> Optional[CurrencyBalance]:
        """
        Edit an existing currency balance's details.

        :param balance_id: ID of the currency balance to be updated.
        :param balance: new balance of the currency (optional).
        :param character_id: character id (optional).
        :param currency_type_id: currency type id (optional).
        :return: updated currency balance instance or None.
        """
        currency_balance = await self.get_currency_balance_by_id(balance_id)
        if not currency_balance:
            return None
        await currency_balance.fetch_related(
            "character",
            "currency_type",
        )

        if balance is not None:
            currency_balance.balance = balance
        if character_id is not None:
            character = await Character.get(id=character_id)
            if character:
                currency_balance.character = character
        if currency_type_id is not None:
            currency_type = await CurrencyType.get(id=currency_type_id)
            if currency_type:
                currency_balance.currency_type = currency_type

        await currency_balance.save()
        return currency_balance
