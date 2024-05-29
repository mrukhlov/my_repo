from typing import List, Optional

from test_task.db.models.models import CurrencyType


class CurrencyTypeDAO:
    """Class for accessing the currency type table."""

    async def create_currency_type(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> CurrencyType:
        """
        Add single currency type to the database.

        :param name: name of the currency type.
        :param description: description of the currency type.
        :return: currency_type object.
        """
        return await CurrencyType.create(
            name=name,
            description=description,
        )

    async def get_currency_type_by_id(self, type_id: int) -> Optional[CurrencyType]:
        """
        Get currency type by ID.

        :param type_id: ID of the currency type.
        :return: currency type instance or None.
        """
        return await CurrencyType.filter(id=type_id).first()

    async def get_all_currency_types(
        self,
        limit: int,
        offset: int,
    ) -> List[CurrencyType]:
        """
        Get all currency types with limit/offset pagination.

        :param limit: limit of currency types.
        :param offset: offset of currency types.
        :return: list of currency types.
        """
        return await CurrencyType.all().offset(offset).limit(limit)

    async def filter_currency_types(
        self,
        name: Optional[str] = None,
    ) -> List[CurrencyType]:
        """
        Get specific currency type models.

        :param name: name of currency type instance.
        :return: currency type models.
        """
        query = CurrencyType.all()
        if name:
            query = query.filter(name=name)
        return await query

    async def edit_currency_type(
        self,
        type_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[CurrencyType]:
        """
        Edit an existing currency type's details.

        :param type_id: ID of the currency type to be updated.
        :param name: new name of the currency type (optional).
        :param description: new description of the currency type (optional).
        :return: updated currency type instance or None if currency type not found.
        """
        currency_type = await self.get_currency_type_by_id(type_id)
        if not currency_type:
            return None

        if name is not None:
            currency_type.name = name
        if description is not None:
            currency_type.description = description

        await currency_type.save()
        return currency_type
