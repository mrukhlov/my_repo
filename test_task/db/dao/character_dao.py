from typing import List, Optional

from test_task.db.models.models import Character


class CharacterDAO:
    """Class for accessing the character table."""

    async def create_character(
        self,
        name: str,
        user_id: int,
        level: int = 1,
        experience: int = 0,
    ) -> Character:
        """
        Add single character to the database.

        :param name: name of the character.
        :param user_id: ID of the user who owns the character.
        :param level: level of the character.
        :param experience: experience points of the character.
        :return: character instance
        """
        return await Character.create(
            name=name,
            user_id=user_id,
            level=level,
            experience=experience,
        )

    async def get_character_by_id(self, character_id: int) -> Optional[Character]:
        """
        Get a character by ID.

        :param character_id: ID of the character.
        :return: character instance or None.
        """
        return (
            await Character.filter(id=character_id)
            .prefetch_related(
                "user",
            )
            .first()
        )

    async def get_all_characters(self, limit: int, offset: int) -> List[Character]:
        """
        Get all characters with limit/offset pagination.

        :param limit: limit of characters.
        :param offset: offset of characters.
        :return: list of characters.
        """
        return await Character.all().offset(offset).limit(limit)

    async def filter_characters(
        self,
        name: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> List[Character]:
        """
        Get specific character models.

        :param name: name of character instance.
        :param user_id: ID of user who owns the character.
        :return: character models.
        """
        filters = {}
        if name:
            filters["name"] = name
        if user_id:
            filters["user_id"] = user_id  # type: ignore
        return await Character.filter(**filters).all()

    async def edit_character(
        self,
        character_id: int,
        name: Optional[str] = None,
        level: Optional[int] = None,
        experience: Optional[int] = None,
    ) -> Optional[Character]:
        """
        Edit an existing character's details.

        :param character_id: ID of the character to be updated.
        :param name: new name of the character (optional).
        :param level: new level of the character (optional).
        :param experience: new experience points of the character (optional).
        :return: updated character instance or None if character not found.
        """
        character = await self.get_character_by_id(character_id)
        if not character:
            return None

        if name is not None:
            character.name = name
        if level is not None:
            character.level = level
        if experience is not None:
            character.experience = experience

        await character.save()
        return character
