from typing import List, Optional

from tortoise.exceptions import ValidationError

from test_task.db.models.models import Character, Equipment


class EquipmentDAO:
    """Class for accessing the equipment table."""

    async def create_equipment(
        self,
        name: str,
        eq_type: str,
        character_id: int,
        eq_slot: str,
        power: int = 0,
        equipped: bool = False,
    ) -> Equipment:
        """
        Add single equipment to the database.

        :param name: name of the equipment.
        :param eq_type: type of the equipment (e.g., "armor", "weapon").
        :param character_id: ID of the character who owns the equipment.
        :param power: power of the equipment.
        :param eq_slot: eq_slot of the equipment.
        :param equipped: equipped flag of the equipment.
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
        )
        await equipment.fetch_related("character")
        return equipment

    async def get_equipment_by_id(self, equipment_id: int) -> Optional[Equipment]:
        """
        Get equipment by ID.

        :param equipment_id: ID of the equipment.
        :return: equipment instance or None.
        """
        equipment = await Equipment.filter(id=equipment_id).first()
        if equipment:
            await equipment.fetch_related("character")
        return equipment

    async def get_all_equipment(self, limit: int, offset: int) -> List[Equipment]:
        """
        Get all equipment with limit/offset pagination.

        :param limit: limit of equipment.
        :param offset: offset of equipment.
        :return: list of equipment.
        """
        return await Equipment.all().offset(offset).limit(limit)

    async def filter_equipment(
        self,
        name: Optional[str] = None,
        eq_type: Optional[str] = None,
        character_id: Optional[int] = None,
    ) -> List[Equipment]:
        """
        Get specific equipment models.

        :param name: name of equipment instance.
        :param eq_type: type of equipment (e.g., "armor", "weapon").
        :param character_id: ID of character who owns the equipment.
        :return: equipment models.
        """
        filters = {}
        if name:
            filters["name"] = name
        if eq_type:
            filters["type"] = eq_type  # type: ignore
        if character_id:
            filters["character_id"] = character_id  # type: ignore
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
        :raises ValidationError: HTTPException
        :return: updated equipment instance or None if equipment not found.
        """
        equipment = await self.get_equipment_by_id(equipment_id)
        if not equipment:
            return None
        await equipment.fetch_related(
            "character",
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
        if eq_slot is not None:
            equipment.slot = eq_slot  # type: ignore
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
