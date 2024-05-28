from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends

from test_task.db.dao.user_profile_dao import UserProfileDAO
from test_task.db.models.models import UserProfile
from test_task.web.api.user_profile.schema import (
    UserProfileModelDTO,
    UserProfileModelInputDTO,
)

router = APIRouter()


@router.get("/", response_model=List[UserProfileModelDTO])
async def get_user_profile_models(
    limit: int = 10,
    offset: int = 0,
    user_profile_dao: UserProfileDAO = Depends(),
) -> List[UserProfile]:
    """
    Retrieve all user_profile objects from the database.

    :param limit: limit of user_profile objects, defaults to 10.
    :param offset: offset of user_profile objects, defaults to 0.
    :param user_profile_dao: DAO for user_profile models.
    :return: list of user_profile objects from database.
    """
    return await user_profile_dao.get_all_user_profiles(limit=limit, offset=offset)


@router.get("/{user_profile_id}/", response_model=UserProfileModelDTO)
async def get_user_profile_model(
    user_profile_id: int,
    user_profile_dao: UserProfileDAO = Depends(),
) -> UserProfileModelDTO:
    """
    Retrieve user_profile object from the database.

    :param user_profile_id: user_profile_id.
    :param user_profile_dao: DAO for user_profile models.
    :return: user_profile object from database.
    """
    user_profile = await user_profile_dao.get_user_profile_by_id(
        profile_id=user_profile_id,
    )
    return UserProfileModelDTO.model_validate(user_profile)


@router.put("/{user_profile_id}/")
async def edit_user_profile_model(
    user_profile_id: int,
    new_user_profile_object: UserProfileModelInputDTO,
    user_profile_dao: UserProfileDAO = Depends(),
) -> None:
    """
    Edits user_profile model in the database.

    :param user_profile_id: user_profile_id.
    :param new_user_profile_object: new user_profile model item.
    :param user_profile_dao: DAO for user_profile models.
    """
    await user_profile_dao.edit_user_profile(
        profile_id=user_profile_id,
        bio=new_user_profile_object.bio,
        avatar_url=new_user_profile_object.avatar_url,
        location=new_user_profile_object.location,
    )


@router.post("/", response_model=UserProfileModelDTO)
async def create_user_profile_model(
    new_user_profile_object: UserProfileModelInputDTO,
    user_profile_dao: UserProfileDAO = Depends(),
) -> UserProfileModelDTO:
    """
    Creates user_profile model in the database.

    :param new_user_profile_object: new user_profile model item.
    :param user_profile_dao: DAO for user_profile models.
    :return: user profile
    """
    user_profile = await user_profile_dao.create_user_profile(
        user_id=new_user_profile_object.user_id,
        bio=new_user_profile_object.bio,
        avatar_url=new_user_profile_object.avatar_url,
        location=new_user_profile_object.location,
    )
    return UserProfileModelDTO.model_validate(user_profile)


@router.delete("/{user_profile_id}/")
async def delete_user_profile_model(
    user_profile_id: int,
    user_profile_dao: UserProfileDAO = Depends(),
) -> None:
    """
    Deletes user_profile model in the database.

    :param user_profile_id: user_profile id.
    :param user_profile_dao: DAO for user_profile models.
    """
    user_profile = await user_profile_dao.get_user_profile_by_id(user_profile_id)
    if user_profile:
        await user_profile.delete()
