from collections.abc import Sequence

from sqlmodel import Session, select

from models_all.group import Group, GroupCreate, GroupUpdate
from repositories.group_repository import GroupRepository
from utils.pagination import PaginationParams


class GroupService:
    def __init__(self, session: Session, repository: GroupRepository):
        self.session = session
        self.repository = repository

    def get_groups_of_user(
        self, user_id: int, params: PaginationParams
    ) -> tuple[Sequence[Group], int]:
        """
        Get the groups belonging to a specific user.

        :param user_id: The ID of the user
        :param params: Pagination parameters
        :return: A tuple containing a sequence of Groups and the total count
        """
        return self.repository.get_groups_of_user(self.session, user_id, params)

    async def get_admin_statuses(self, groups: Sequence[Group], user) -> list[bool]:
        """
        Get the admin statuses of a user for a sequence of groups concurrently.

        :param groups: A sequence of Group objects to check
        :param user: The TelegramUser object representing the current user
        :return: A list of boolean values indicating admin status in the respective groups
        """
        import asyncio

        from api.auth_deps import is_group_admin
        admin_tasks = [is_group_admin(g, user, self.session) for g in groups]
        return await asyncio.gather(*admin_tasks)

    def remove_user_from_group(self, group_id: int, user_id: int) -> None:
        """
        Remove a user from a specific group.

        :param group_id: The ID of the group
        :param user_id: The ID of the user to remove
        """
        return self.repository.remove_user_from_group(self.session, group_id, user_id)

    @staticmethod
    def get_or_create_group(session: Session, group_in: GroupCreate) -> Group:
        """
        Get an existing group or create it if it doesn't exist.
        If it exists, updates it with the provided information.

        :param session: The database session
        :param group_in: The GroupCreate schema containing the group's details
        :return: The existing or newly created Group object
        """
        group_repo = GroupRepository()
        statement = select(Group).where(Group.telegram_id == int(group_in.telegram_id))
        group = session.exec(statement).first()
        if not group:
            group = Group.model_validate(group_in)
            group_repo.create(session, group)
        else:
            group_update = GroupUpdate(
                telegram_id=group_in.telegram_id,
                group_name=group_in.group_name,
                group_description=group_in.group_description,
                group_username=group_in.group_username,
                group_type=group_in.group_type,
                group_members=group_in.group_members,
            )
            group_repo.update(
                session, group, group_update.model_dump(exclude_unset=True)
            )
        return group

    @staticmethod
    def get_all_groups(session: Session) -> Sequence[Group]:
        """
        Get all groups in the database.

        :param session: The database session
        :return: A sequence of Group objects
        """
        return GroupRepository().get_all(session)

    @staticmethod
    def update_group(session: Session, telegram_id: int, **kwargs) -> Group | None:
        """
        Update an existing group based on its Telegram ID.

        :param session: The database session
        :param telegram_id: The Telegram ID of the group
        :param kwargs: The fields to update
        :return: The updated Group object, or None if not found
        """
        repo = GroupRepository()
        group = repo.get_by_telegram_id(session, telegram_id)
        if group:
            return repo.update(session, group, kwargs)
        return None

    @staticmethod
    def delete_group(session: Session, telegram_id: int) -> None:
        """
        Delete a group based on its Telegram ID.

        :param session: The database session
        :param telegram_id: The Telegram ID of the group to delete
        """
        repo = GroupRepository()
        group = repo.get_by_telegram_id(session, telegram_id)
        if group:
            repo.delete(session, group.id)
