import asyncio
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlmodel import Session, select

from models_all.group import Group, GroupCreate, GroupUpdate
from models_all.group_setting import GroupSetting
from models_all.group_setting_tag_list_link import GroupSettingTagListLink
from models_all.tag_list import TagList
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from services.base_service import BaseService
from services.cache_service import CacheService
from services.log_service import LogService
from utils.languages import SUPPORTED_LANGUAGES, is_supported
from utils.pagination import PaginationParams


class GroupService(BaseService):
    def __init__(
        self,
        session: Session,
        repository: GroupRepository,
        log_service: LogService | None = None,
        cache: CacheService | None = None,
    ):
        """:param session: SQLModel session.
        :param repository: :class:`GroupRepository` for group access.
        :param log_service: optional audit log writer.
        :param cache: optional cache service.
        """
        super().__init__(session=session, log_service=log_service, cache=cache)
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
        from api.auth_deps import is_group_admin  # local import: breaks circular dep

        admin_tasks = [is_group_admin(g, user, self.session) for g in groups]
        return await asyncio.gather(*admin_tasks)

    def remove_user_from_group(self, group_id: uuid.UUID, user_id: int) -> None:
        """
        Remove a user from a specific group.

        :param group_id: The internal ID of the group (UUID)
        :param user_id: The ID of the user to remove
        """
        return self.repository.remove_user_from_group(self.session, group_id, user_id)

    def get_group_settings(self, group_id: uuid.UUID) -> GroupSetting:
        """
        Get or create settings for a specific group.
        """
        group = self.repository.get_by_id(self.session, group_id)
        if not group:
            raise ValueError("Group not found")

        settings = self.repository.get_settings(self.session, group_id)
        if not settings:
            settings = GroupSetting(group_id=group_id)
        return settings

    def update_group_settings(
        self, group_id: uuid.UUID, update_data: dict
    ) -> GroupSetting:
        """
        Update settings for a specific group with validation.
        """
        group = self.repository.get_by_id(self.session, group_id)
        if not group:
            raise ValueError("Group not found")

        settings = self.repository.get_settings(self.session, group_id)
        if not settings:
            settings = self.repository.create_settings(self.session, group_id)

        if "language" in update_data and update_data["language"] is not None:
            if not is_supported(update_data["language"]):
                raise ValueError(
                    f"Unsupported language. Choose one of: {', '.join(SUPPORTED_LANGUAGES)}"
                )

        if "auto_add_list_ids" in update_data:
            list_ids = update_data.pop("auto_add_list_ids")
            if list_ids is not None:
                list_repo = ListRepository()

                valid_lids = []
                for lid in list_ids:
                    tag_list = list_repo.get_by_id(self.session, lid)
                    if not tag_list or tag_list.group_id != group_id:
                        raise ValueError(f"Invalid list ID {lid} for this group")
                    valid_lids.append(uuid.UUID(str(lid)))

                statement = select(GroupSettingTagListLink).where(
                    GroupSettingTagListLink.group_setting_id == settings.id
                )
                existing_links = self.session.exec(statement).all()

                existing_lids = {link.tag_list_id for link in existing_links}
                new_lids = set(valid_lids)

                for link in existing_links:
                    if link.tag_list_id not in new_lids:
                        link.active = False
                        link.deleted_at = datetime.now(UTC)
                        self.session.add(link)
                    else:
                        link.active = True
                        link.deleted_at = None
                        self.session.add(link)

                for lid in new_lids - existing_lids:
                    new_link = GroupSettingTagListLink(
                        group_setting_id=settings.id, tag_list_id=lid
                    )
                    self.session.add(new_link)

                self.session.commit()

        new_language = update_data.get("language")
        old_language = settings.language
        telegram_id = group.telegram_id

        updated = self.repository.update_settings(self.session, settings, update_data)

        # If the reply language changed, refresh this group's localized
        # slash-command menu (chat scope). Best-effort; never blocks the update.
        if new_language and new_language != old_language:
            from bot.utils.commands_sync import set_chat_commands

            set_chat_commands(telegram_id, new_language)

        return updated

    @staticmethod
    def _ensure_everyone_list(session: Session, group: Group) -> None:
        list_repo = ListRepository()
        everyone_list = list_repo.get_by_trigger_name(session, group.id, "everyone")
        if not everyone_list:
            new_list = TagList(
                group_id=group.id,
                name="Everyone",
                trigger_name="everyone",
                description="Default list for everyone in the group",
                aliases=["all"],
                is_system=True,
            )
            list_repo.create(session, new_list)

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
        GroupService._ensure_everyone_list(session, group)
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
            updated_group = repo.update(session, group, kwargs)
            GroupService._ensure_everyone_list(session, updated_group)
            return updated_group
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
