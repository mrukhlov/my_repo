from typing import List, Optional

from test_task.db.models.models import UserProfile


class UserProfileDAO:
    """Class for accessing the user profile table."""

    async def create_user_profile(
        self,
        user_id: int,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
        location: Optional[str] = None,
    ) -> UserProfile:
        """
        Add single user profile to the database.

        :param user_id: ID of the user who owns the profile.
        :param bio: bio of the user.
        :param avatar_url: avatar URL of the user.
        :param location: location of the user.
        :return: user instance
        """
        return await UserProfile.create(
            user_id=user_id,
            bio=bio,
            avatar_url=avatar_url,
            location=location,
        )

    async def get_user_profile_by_id(self, profile_id: int) -> Optional[UserProfile]:
        """
        Get user profile by ID.

        :param profile_id: ID of the user profile.
        :return: user profile instance or None.
        """
        return await UserProfile.filter(id=profile_id).first()

    async def get_all_user_profiles(self, limit: int, offset: int) -> List[UserProfile]:
        """
        Get all user profiles with limit/offset pagination.

        :param limit: limit of user profiles.
        :param offset: offset of user profiles.
        :return: list of user profiles.
        """
        return await UserProfile.all().offset(offset).limit(limit)

    async def filter_user_profiles(
        self,
        user_id: Optional[int] = None,
    ) -> List[UserProfile]:
        """
        Get specific user profile models.

        :param user_id: ID of user who owns the profile.
        :return: user profile models.
        """
        query = UserProfile.all()
        if user_id:
            query = query.filter(user_id=user_id)
        return await query

    async def edit_user_profile(
        self,
        profile_id: int,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Optional[UserProfile]:
        """
        Edit an existing user profile's details.

        :param profile_id: ID of the user profile to be updated.
        :param bio: new bio of the user (optional).
        :param avatar_url: new avatar URL of the user (optional).
        :param location: new location of the user (optional).
        :return: updated user profile instance or None if profile not found.
        """
        profile = await self.get_user_profile_by_id(profile_id)
        if not profile:
            return None

        if bio is not None:
            profile.bio = bio
        if avatar_url is not None:
            profile.avatar_url = avatar_url
        if location is not None:
            profile.location = location

        await profile.save()
        return profile
