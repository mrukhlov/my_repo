from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends

from test_task.db.dao.user_dao import UserDAO
from test_task.db.models.models import User
from test_task.web.api.user.schema import UserModelDTO, UserModelInputDTO

router = APIRouter()


@router.get("/", response_model=List[UserModelDTO])
async def get_user_models(
    limit: int = 10,
    offset: int = 0,
    user_dao: UserDAO = Depends(),
) -> List[User]:
    """
    Retrieve all user objects from the database.

    :param limit: limit of user objects, defaults to 10.
    :param offset: offset of user objects, defaults to 0.
    :param user_dao: DAO for user models.
    :return: list of user objects from database.
    """
    return await user_dao.get_all_users(limit=limit, offset=offset)


@router.put("/{user_id}/")
async def edit_user_model(
    user_id: int,
    new_user_object: UserModelInputDTO,
    user_dao: UserDAO = Depends(),
) -> None:
    """
    Edits user model in the database.

    :param user_id: user_id.
    :param new_user_object: new user model item.
    :param user_dao: DAO for user models.
    """
    await user_dao.edit_user(
        user_id=user_id,
        username=new_user_object.username,
        email=new_user_object.email,
        password_hash=new_user_object.password_hash,
    )


@router.delete("/{user_id}/")
async def delete_user_model(
    user_id: int,
    user_dao: UserDAO = Depends(),
) -> None:
    """
    Deletes user model in the database.

    :param user_id: user id.
    :param user_dao: DAO for user models.
    """
    user = await user_dao.get_user_by_id(user_id)
    if user:
        await user.delete()


@router.post("/", response_model=UserModelDTO)
async def create_user_model(
    new_user_object: UserModelInputDTO,
    user_dao: UserDAO = Depends(),
) -> UserModelDTO:
    """
    Creates user model in the database.

    :param new_user_object: new user model item.
    :param user_dao: DAO for user models.
    :return: user model
    """
    user = await user_dao.create_user(
        username=new_user_object.username,
        email=new_user_object.email,
        password_hash=new_user_object.password_hash,
    )
    return UserModelDTO.model_validate(user)
