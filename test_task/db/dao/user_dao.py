from typing import List, Optional

from test_task.db.models.models import User


class UserDAO:
    """Class for accessing the user table."""

    async def create_user(self, username: str, email: str, password_hash: str) -> User:
        """
        Add single user to the database.

        :param username: username of the user.
        :param email: email of the user.
        :param password_hash: password hash of the user.
        :return: user instance.
        """
        return await User.create(
            username=username,
            email=email,
            password_hash=password_hash,
        )

    async def edit_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password_hash: Optional[str] = None,
    ) -> Optional[User]:
        """
        Edit an existing user's details.

        :param user_id: ID of the user to be updated.
        :param username: new username of the user (optional).
        :param email: new email of the user (optional).
        :param password_hash: new password hash of the user (optional).
        :return: updated user instance or None if user not found.
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if password_hash is not None:
            user.password_hash = password_hash

        await user.save()
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.

        :param user_id: ID of the user.
        :return: user instance or None.
        """
        return await User.filter(id=user_id).first()

    async def get_all_users(self, limit: int, offset: int) -> List[User]:
        """
        Get all users with limit/offset pagination.

        :param limit: limit of users.
        :param offset: offset of users.
        :return: list of users.
        """
        return await User.all().offset(offset).limit(limit)

    async def filter_users(
        self,
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> List[User]:
        """
        Get specific user models.

        :param username: username of user instance.
        :param email: email of user instance.
        :return: user models.
        """
        filters = {}
        if username:
            filters["username"] = username
        if email:
            filters["email"] = email  # type: ignore
        return await User.filter(**filters).all()
