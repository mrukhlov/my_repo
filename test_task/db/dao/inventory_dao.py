from typing import List, Optional

from test_task.db.models.models import Character, Inventory


class InventoryDAO:
    """Class for accessing the inventory table."""

    async def create_inventory(
        self,
        character_id: int,
        item_name: str,
        item_type: str,
        quantity: int = 1,
    ) -> Inventory:
        """
        Add single inventory item to the database.

        :param character_id: ID of the character who owns the inventory item.
        :param item_name: name of the item.
        :param item_type: type of the item (e.g., "potion", "scroll").
        :param quantity: quantity of the item.
        :return: inventory instance
        """
        inventory = await Inventory.create(
            character_id=character_id,
            item_name=item_name,
            item_type=item_type,
            quantity=quantity,
        )
        await inventory.fetch_related("character")
        return inventory

    async def get_inventory_by_id(self, inventory_id: int) -> Optional[Inventory]:
        """
        Get inventory by ID.

        :param inventory_id: ID of the inventory.
        :return: inventory instance or None.
        """
        inventory = await Inventory.filter(id=inventory_id).first()
        if inventory:
            await inventory.fetch_related("character")
        return inventory

    async def get_all_inventory(self, limit: int, offset: int) -> List[Inventory]:
        """
        Get all inventory items with limit/offset pagination.

        :param limit: limit of inventory items.
        :param offset: offset of inventory items.
        :return: list of inventory items.
        """
        return await Inventory.all().offset(offset).limit(limit)

    async def filter_inventory(
        self,
        character_id: Optional[int] = None,
        item_name: Optional[str] = None,
        item_type: Optional[str] = None,
    ) -> List[Inventory]:
        """
        Get specific inventory models.

        :param character_id: ID of character who owns the inventory.
        :param item_name: name of the item.
        :param item_type: type of the item.
        :return: inventory models.
        """
        filters = {}
        if character_id:
            filters["character_id"] = character_id
        if item_name:
            filters["item_name"] = item_name  # type: ignore
        if item_type:
            filters["item_type"] = item_type  # type: ignore
        return await Inventory.filter(**filters).all()

    async def edit_inventory(  # noqa: C901, WPS211
        self,
        inventory_id: int,
        character_id: Optional[int] = None,
        item_name: Optional[str] = None,
        item_type: Optional[str] = None,
        quantity: Optional[int] = None,
    ) -> Optional[Inventory]:
        """
        Edit an existing inventory item's details.

        :param inventory_id: ID of the inventory item to be updated.
        :param character_id: new ID of the character (optional).
        :param item_name: new name of the item (optional).
        :param item_type: new type of the item (optional).
        :param quantity: new quantity of the item (optional).
        :return: updated inventory instance or None if inventory item not found.
        """
        inventory = await self.get_inventory_by_id(inventory_id)
        if not inventory:
            return None
        await inventory.fetch_related(
            "character",
        )

        if character_id is not None:
            character = await Character.filter(id=character_id).first()
            if character:
                inventory.character_id = character.id  # type: ignore
        if item_name is not None:
            inventory.item_name = item_name
        if item_type is not None:
            inventory.item_type = item_type
        if quantity is not None:
            inventory.quantity = quantity

        await inventory.save()
        return inventory
