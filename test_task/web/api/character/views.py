from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends

from test_task.db.dao.character_dao import CharacterDAO
from test_task.db.models.models import Character
from test_task.web.api.character.schema import CharacterModelDTO, CharacterModelInputDTO

router = APIRouter()


@router.get("/", response_model=List[CharacterModelDTO])
async def get_character_models(
    limit: int = 10,
    offset: int = 0,
    character_dao: CharacterDAO = Depends(),
) -> List[Character]:
    """
    Retrieve all character objects from the database.

    :param limit: limit of character objects, defaults to 10.
    :param offset: offset of character objects, defaults to 0.
    :param character_dao: DAO for character models.
    :return: list of character objects from database.
    """
    return await character_dao.get_all_characters(limit=limit, offset=offset)


@router.get("/{character_id}/", response_model=CharacterModelDTO)
async def get_character_model(
    character_id: int,
    character_dao: CharacterDAO = Depends(),
) -> CharacterModelDTO:
    """
    Retrieve character object from the database.

    :param character_id: character_id.
    :param character_dao: DAO for character models.
    :return: character object from database.
    """
    character = await character_dao.get_character_by_id(
        character_id=character_id,
    )
    return CharacterModelDTO.model_validate(character)


@router.put("/{character_id}/")
async def edit_character_model(
    character_id: int,
    new_character_object: CharacterModelInputDTO,
    character_dao: CharacterDAO = Depends(),
) -> None:
    """
    Edits character model in the database.

    :param character_id: character_id.
    :param new_character_object: new character model item.
    :param character_dao: DAO for character models.
    """
    await character_dao.edit_character(
        character_id=character_id,
        name=new_character_object.name,
        level=new_character_object.level,
        experience=new_character_object.experience,
    )


@router.post("/")
async def create_character_model(
    new_character_object: CharacterModelInputDTO,
    character_dao: CharacterDAO = Depends(),
) -> None:
    """
    Creates character model in the database.

    :param new_character_object: new character model item.
    :param character_dao: DAO for character models.
    """
    await character_dao.create_character(
        name=new_character_object.name,
        user_id=new_character_object.user_id,
        level=new_character_object.level,
        experience=new_character_object.experience,
    )


@router.delete("/{character_id}/")
async def delete_character_model(
    character_id: int,
    character_dao: CharacterDAO = Depends(),
) -> None:
    """
    Deletes character model in the database.

    :param character_id: character id.
    :param character_dao: DAO for character models.
    """
    character = await character_dao.get_character_by_id(character_id)
    if character:
        await character.delete()
