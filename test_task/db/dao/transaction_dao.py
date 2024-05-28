from typing import List, Optional

from test_task.db.models.models import Character, CurrencyType, Equipment, Transaction


class TransactionDAO:
    """Class for accessing the transaction table."""

    async def create_transaction(  # noqa: WPS211
        self,
        transaction_type: str,
        amount: int,
        item_id: int,
        currency_type_id: int,
        character_from_id: int,
        character_to_id: int,
    ) -> Transaction:
        """
        Add single transaction to the database.

        :param transaction_type: type of the transaction (e.g., "purchase", "sale").
        :param amount: amount involved in the transaction.
        :param item_id: ID of the item involved in the transaction.
        :param currency_type_id: ID of the currency type used in the transaction.
        :param character_from_id: ID of the character who initiated the transaction.
        :param character_to_id: ID of the character who received the transaction.
        :return: transaction model
        """
        transaction = await Transaction.create(
            transaction_type=transaction_type,
            amount=amount,
            item_id=item_id,
            currency_type_id=currency_type_id,
            character_from_id=character_from_id,
            character_to_id=character_to_id,
        )
        await transaction.fetch_related(
            "item",
            "currency_type",
            "character_from",
            "character_to",
        )
        return transaction

    async def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """
        Get transaction by ID.

        :param transaction_id: ID of the transaction.
        :return: transaction instance or None.
        """
        return (
            await Transaction.filter(id=transaction_id)
            .prefetch_related(
                "character_from",
                "character_to",
                "item",
                "currency_type",
            )
            .first()
        )

    async def get_all_transactions(self, limit: int, offset: int) -> List[Transaction]:
        """
        Get all transactions with limit/offset pagination.

        :param limit: limit of transactions.
        :param offset: offset of transactions.
        :return: list of transactions.
        """
        return await Transaction.all().offset(offset).limit(limit)

    async def filter_transactions(
        self,
        transaction_type: Optional[str] = None,
        character_from_id: Optional[int] = None,
        character_to_id: Optional[int] = None,
    ) -> List[Transaction]:
        """
        Get specific transaction models.

        :param transaction_type: type of the transaction.
        :param character_from_id: ID of the character who initiated the transaction.
        :param character_to_id: ID of the character who received the transaction.
        :return: transaction models.
        """
        filters = {}
        if transaction_type:
            filters["transaction_type"] = transaction_type
        if character_from_id:
            filters["character_from_id"] = character_from_id  # type: ignore
        if character_to_id:
            filters["character_to_id"] = character_to_id  # type: ignore
        return await Transaction.filter(**filters).all()

    async def edit_transaction(  # noqa: C901, WPS211, WPS217, WPS231
        self,
        transaction_id: int,
        transaction_type: Optional[str] = None,
        amount: Optional[int] = None,
        item_id: Optional[int] = None,
        currency_type_id: Optional[int] = None,
        character_from_id: Optional[int] = None,
        character_to_id: Optional[int] = None,
    ) -> Optional[Transaction]:
        """
        Edit an existing transaction's details.

        :param transaction_id: ID of the transaction to be updated.
        :param transaction_type: new type of the transaction (optional).
        :param amount: new amount involved in the transaction (optional).
        :param item_id: new ID of the item (optional).
        :param currency_type_id: ID of the currency type (optional).
        :param character_from_id: ID of the character (optional).
        :param character_to_id: ID of the character (optional).
        :return: updated transaction instance or None if transaction not found.
        """
        transaction = await self.get_transaction_by_id(transaction_id)
        if not transaction:
            return None
        await transaction.fetch_related(
            "item",
            "currency_type",
            "character_from",
            "character_to",
        )

        if transaction_type is not None:
            transaction.transaction_type = transaction_type
        if amount is not None:
            transaction.amount = amount
        if item_id is not None:
            item = await Equipment.get(id=item_id)
            if item:
                transaction.item = item  # type: ignore
        if currency_type_id is not None:
            currency_type = await CurrencyType.get(id=currency_type_id)
            if currency_type:
                transaction.currency_type = currency_type  # type: ignore
        if character_from_id is not None:
            character_from = await Character.get(id=character_from_id)
            if character_from:
                transaction.character_from = character_from  # type: ignore
        if character_to_id is not None:
            character_to = await Character.get(id=character_from_id)
            if character_to:
                transaction.character_from = character_to  # type: ignore

        await transaction.save()
        return transaction
