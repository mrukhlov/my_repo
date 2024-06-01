from typing import Any, Dict, List, Optional

import tortoise
from loguru import logger
from tortoise.exceptions import ValidationError

from test_task.db.models.models import Character, CurrencyType, Equipment


class EquipmentDAO:
    """Equipment DAO class."""

    using_db: Optional[tortoise.BaseDBAsyncClient] = None

    async def create_equipment(
        self,
        name: str,
        eq_type: str,
        character_id: int,
        eq_slot: str,
        currency_type_id: int,
        power: int = 0,
        equipped: bool = False,
        price: float = 0.00,
        quantity: int = 1,
    ) -> Equipment:
        """
        Add single equipment to the database.

        :param name: name of the equipment.
        :param eq_type: type of the equipment (e.g., "armor", "weapon").
        :param character_id: ID of the character who owns the equipment.
        :param power: power of the equipment.
        :param eq_slot: eq_slot of the equipment.
        :param equipped: equipped flag of the equipment.
        :param price: price of the equipment.
        :param currency_type_id: currency_type_id of the equipment.
        :param quantity: quantity of the equipment.
        :return: equipment instance
        """
        if equipped:
            existing_equipped = await Equipment.filter(
                character_id=character_id,
                slot=eq_slot,
                equipped=True,
            ).exists()
            if existing_equipped:
                equipped = False

        equipment = await Equipment.create(
            name=name,
            type=eq_type,
            character_id=character_id,
            power=power,
            slot=eq_slot,
            equipped=equipped,
            currency_type_id=currency_type_id,
            price=price,
            quantity=quantity,
        )
        await equipment.fetch_related(
            "character",
            "currency_type",
        )
        return equipment

    async def get_equipment_by_id(self, equipment_id: int) -> Optional[Equipment]:
        """
        Get equipment by ID.

        :param equipment_id: ID of the equipment.
        :return: equipment instance or None.
        """
        equipment = await Equipment.filter(id=equipment_id).first()
        if equipment:
            await equipment.fetch_related(
                "character",
                "currency_type",
            )
        return equipment

    async def get_all_equipment(self, limit: int, offset: int) -> List[Equipment]:
        """
        Get all equipment with limit/offset pagination.

        :param limit: limit of equipment.
        :param offset: offset of equipment.
        :return: list of equipment.
        """
        return await Equipment.all().offset(offset).limit(limit)

    async def filter_equipment(  # noqa: C901
        self,
        equipment_id: Optional[int] = None,
        name: Optional[str] = None,
        eq_type: Optional[str] = None,
        character_id: Optional[int] = None,
        eq_slot: Optional[str] = None,
        currency_type_id: Optional[int] = None,
        power: Optional[int] = None,
        equipped: Optional[bool] = None,
        price: Optional[float] = None,
    ) -> List[Equipment]:
        """
        Get specific equipment models.

        :param equipment_id: id of equipment instance.
        :param name: name of equipment instance.
        :param eq_type: type of equipment (e.g., "armor", "weapon").
        :param character_id: ID of character who owns the equipment.
        :param power: power of the equipment.
        :param eq_slot: eq_slot of the equipment.
        :param equipped: equipped flag of the equipment.
        :param price: price of the equipment.
        :param currency_type_id: currency_type_id of the equipment.
        :return: equipment models.
        """
        filters: Dict[str, Any] = {}
        if equipment_id:
            filters["id"] = equipment_id
        if name:
            filters["name"] = name
        if eq_type:
            filters["type"] = eq_type
        if character_id:
            filters["character_id"] = character_id
        if eq_slot:
            filters["slot"] = eq_slot
        if currency_type_id:
            filters["currency_type_id"] = currency_type_id
        if power is not None:
            filters["power"] = power
        if equipped is not None:
            filters["equipped"] = equipped
        if price is not None:
            filters["price"] = price
        return await Equipment.filter(**filters).all()

    async def edit_equipment(  # noqa: C901, WPS211
        self,
        equipment_id: int,
        name: Optional[str] = None,
        eq_type: Optional[str] = None,
        character_id: Optional[int] = None,
        power: Optional[int] = None,
        eq_slot: Optional[str] = None,
        equipped: Optional[bool] = None,
        price: Optional[float] = None,
        currency_type_id: Optional[int] = None,
    ) -> Optional[Equipment]:
        """
        Edit an existing equipment's details.

        :param equipment_id: ID of the equipment to be updated.
        :param name: new name of the equipment (optional).
        :param eq_type: new type of the equipment (optional).
        :param character_id: new ID of the character who owns the equipment (optional).
        :param power: new power of the equipment (optional).
        :param eq_slot: slot of the equipment.
        :param equipped: equipped flag of the equipment.
        :param price: price of the equipment.
        :param currency_type_id: currency_type_id of the equipment.
        :raises ValidationError: HTTPException
        :return: updated equipment instance or None if equipment not found.
        """
        equipment = await self.get_equipment_by_id(equipment_id)
        if not equipment:
            return None
        await equipment.fetch_related(
            "character",
            "currency_type",
        )

        if name is not None:
            equipment.name = name
        if eq_type is not None:
            equipment.type = eq_type
        if character_id is not None:
            character = await Character.filter(id=character_id).first()
            if character:
                equipment.character = character  # type: ignore
        if power is not None:
            equipment.power = power
        if price is not None:
            equipment.price = price  # type: ignore
        if eq_slot is not None:
            equipment.slot = eq_slot  # type: ignore
        if currency_type_id is not None:
            currency_type = await CurrencyType.filter(
                id=currency_type_id,
            ).first()
            if character:
                equipment.currency_type = currency_type  # type: ignore
        if equipped is not None:
            if equipped:
                existing_equipped = (
                    await Equipment.filter(
                        character=equipment.character,
                        slot=equipment.slot,
                        equipped=True,
                    )
                    .exclude(id=equipment.id)
                    .exists()
                )
                if existing_equipped:
                    raise ValidationError(
                        f"Character already has an equipped {equipment.slot} item.",
                    )
            equipment.equipped = equipped

        await equipment.save()
        return equipment

    async def equip_item(
        self,
        data: Any,
    ) -> None:
        """
        Equip item.

        :param data: data.
        :return: list of equipment.
        """
        try:
            equipment = await Equipment.get(
                id=data.item_id,
                character_id=data.character_id,
                equipped=False,
                using_db=self.using_db,
            )
            if not equipment:
                logger.error("Invalid item_id or already equipped.")
                return
            equipment.equipped = True
            await equipment.save(using_db=self.using_db)
        except tortoise.exceptions.DoesNotExist:
            logger.error("Invalid item_id or already equipped.")

    async def unequip_item(
        self,
        data: Any,
    ) -> None:
        """
        Unequip item.

        :param data: data.
        :return: list of equipment.
        """
        try:
            equipment = await Equipment.get(
                id=data.item_id,
                character_id=data.character_id,
                equipped=True,
                using_db=self.using_db,
            )
            if not equipment:
                logger.error("Invalid item_id or already unequipped.")
                return
            equipment.equipped = False
            await equipment.save(using_db=self.using_db)
        except tortoise.exceptions.DoesNotExist:
            logger.error("Invalid item_id or already unequipped.")
