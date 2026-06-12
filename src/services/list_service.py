import random
import uuid
from collections.abc import Sequence

from sqlmodel import Session
from telegram import Bot, Update

from api.utils.telegram_utils import check_telegram_member
from bot.instance import get_bot
from models_all import ListUser, TagList, TagListCreate, TagListUpdate
from models_all.list_tag_rule import ListTagRuleMode
from models_all.tag_list import TagListWithSubscriptionResponse
from models_all.user import User
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_tag_rule_repository import ListTagRuleRepository
from repositories.list_user_repository import ListUserRepository
from repositories.user_repository import UserRepository
from services.base_service import BaseService
from services.cache_service import CacheService
from services.list_rule_service import ListRuleService
from services.log_service import LogService
from services.member_tag_service import MemberTagService
from services.mention_service import MentionService
from utils.pagination import PaginationParams


class ListService(BaseService):
    def __init__(
        self,
        session: Session,
        repository: ListRepository,
        user_repo: ListUserRepository,
        group_repo: GroupRepository,
        log_service: LogService | None = None,
        cache: CacheService | None = None,
        rule_service: ListRuleService | None = None,
        member_tag_service: MemberTagService | None = None,
    ):
        """:param session: SQLModel session.
        :param repository: :class:`ListRepository` for ``TagList`` access.
        :param user_repo: :class:`ListUserRepository` for membership rows.
        :param group_repo: :class:`GroupRepository` for parent group lookups.
        :param log_service: optional audit log writer; defaults to :class:`LogService`.
        :param cache: optional cache service; defaults to the process singleton.
        :param rule_service: optional :class:`ListRuleService` for tag-rule
            filtering; when omitted a default instance is built lazily.
        :param member_tag_service: optional :class:`MemberTagService` used to
            resolve member tags on the mention path; defaults to a fresh
            instance bound to the shared cache.
        """
        super().__init__(session=session, log_service=log_service, cache=cache)
        self.repository = repository
        self.user_repo = user_repo
        self.group_repo = group_repo
        self.rule_service = rule_service or ListRuleService(
            session=session,
            repository=ListTagRuleRepository(),
            list_repo=repository,
            group_repo=group_repo,
            log_service=log_service,
            cache=cache,
        )
        self.member_tag_service = member_tag_service or MemberTagService(cache=cache)

    def _check_group(self, group_id: uuid.UUID):
        """
        Verify that a group exists in the database.

        :param group_id: The internal ID of the group
        :raises ValueError: If the group is not found
        """
        if not self.group_repo.get_by_id(self.session, group_id):
            raise ValueError("Group not found")

    def get_subscribed_list_ids(self, user_id: int) -> set[uuid.UUID]:
        """
        Get the set of list IDs a user is subscribed to.

        :param user_id: The ID of the user
        :return: A set of subscribed list IDs
        """
        user_subs = self.user_repo.get_user_subscriptions(self.session, user_id)
        return {sub.list_id for sub in user_subs}

    def format_lists_with_subscriptions(
        self,
        lists: Sequence[TagList],
        user_id: int,
        subscribed_list_ids: set[uuid.UUID] | None = None,
        filter_active: bool = False,
    ) -> list:
        """
        Format TagList objects to include subscription status for a specific user.

        :param lists: The sequence of TagList objects to format
        :param user_id: The ID of the user
        :param subscribed_list_ids: An optional pre-fetched set of list IDs the user is subscribed to
        :param filter_active: If True, exclude inactive lists
        :return: A list of TagListWithSubscriptionResponse objects (as dicts or models)
        """

        if subscribed_list_ids is None:
            subscribed_list_ids = self.get_subscribed_list_ids(user_id)

        formatted = []
        for lst in lists:
            if filter_active and not lst.active:
                continue
            data = lst.model_dump()
            data["is_subscribed"] = lst.id in subscribed_list_ids
            formatted.append(TagListWithSubscriptionResponse(**data))
        return formatted

    def get_lists(
        self, group_id: uuid.UUID, params: PaginationParams
    ) -> tuple[Sequence[TagList], int]:
        """
        Get paginated lists for a specific group.

        :param group_id: The internal ID of the group
        :param params: Pagination parameters
        :return: A tuple containing a sequence of TagList objects and the total count
        """
        self._check_group(group_id)
        return self.repository.get_lists_of_group(self.session, group_id, params)

    def create_list(self, user_id: int, obj_in: TagListCreate) -> TagList:
        """
        Create a new list in a group.

        :param user_id: The ID of the user creating the list
        :param obj_in: The TagListCreate schema
        :return: The created TagList object
        """
        self._check_group(obj_in.group_id)
        new_list = self.repository.create(self.session, TagList(**obj_in.model_dump()))
        self._log(
            user_id, obj_in.group_id, "CREATE_LIST", f"Created list {obj_in.name}"
        )
        return new_list

    def get_list_by_trigger_name(self, group_id: uuid.UUID, trigger_name: str):
        """
        Get a list by its trigger name in a specific group.
        """
        self._check_group(group_id)
        return self.repository.get_by_trigger_name(self.session, group_id, trigger_name)

    def get_active_lists(self, group_id: uuid.UUID) -> Sequence[TagList]:
        """Return every active list of a group.

        :param group_id: internal UUID of the group.
        :returns: sequence of active :class:`TagList` rows.
        """
        self._check_group(group_id)
        return self.repository.get_active_for_group(self.session, group_id)

    def update_list(
        self,
        user_id: int,
        group_id: uuid.UUID,
        list_id: uuid.UUID,
        obj_in: TagListUpdate,
    ) -> TagList | None:
        """
        Update an existing list.

        :param user_id: The ID of the user updating the list
        :param group_id: The internal ID of the group
        :param list_id: The internal ID of the list
        :param obj_in: The TagListUpdate schema
        :return: The updated TagList object, or None if not found or group ID mismatch
        """
        self._check_group(group_id)
        tag_list = self.repository.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            return None
        updated = self.repository.update(
            self.session, tag_list, obj_in.model_dump(exclude_unset=True)
        )
        self._log(user_id, group_id, "UPDATE_LIST", f"Updated list {updated.name}")
        return updated

    def delete_list(
        self, user_id: int, group_id: uuid.UUID, list_id: uuid.UUID
    ) -> bool:
        """
        Delete an existing list.

        :param user_id: The ID of the user deleting the list
        :param group_id: The internal ID of the group
        :param list_id: The internal ID of the list
        :return: True if successfully deleted, False if not found or group ID mismatch
        :raises ValueError: If attempting to delete a system list
        """
        self._check_group(group_id)
        tag_list = self.repository.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            return False
        # Cannot delete system list
        if tag_list.is_system:
            raise ValueError("Cannot delete a system list")

        # Cascade soft-delete every membership row in a single UPDATE statement
        # before soft-deleting the parent list. Avoids loading rows into memory
        # for lists with thousands of members.
        self.user_repo.soft_delete_where(self.session, ListUser.list_id == list_id)
        success = self.repository.delete(self.session, list_id)
        if success:
            self._log(user_id, group_id, "DELETE_LIST", f"Deleted list {tag_list.name}")
        return success

    def clear_list(self, user_id: int, group_id: uuid.UUID, list_id: uuid.UUID) -> int:
        """
        Clear all users from a list.

        :param user_id: The ID of the user clearing the list
        :param group_id: The internal ID of the group
        :param list_id: The internal ID of the list
        :return: Number of users cleared, or -1 if not found or group ID mismatch
        """
        self._check_group(group_id)
        tag_list = self.repository.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            return -1

        cleared_count = self.user_repo.clear_list_subscriptions(self.session, list_id)
        self.session.commit()
        self._log(
            user_id,
            group_id,
            "CLEAR_LIST",
            f"Cleared {cleared_count} users from list {tag_list.name}",
        )
        return cleared_count

    def subscribe(self, user_id: int, group_id: uuid.UUID, list_id: uuid.UUID) -> bool:
        """
        Subscribe a user to a list.

        :param user_id: The ID of the user
        :param group_id: The internal ID of the group
        :param list_id: The internal ID of the list
        :return: True if newly subscribed, False if list not found, group ID mismatch, or already subscribed
        """
        self._check_group(group_id)
        tag_list = self.repository.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            return False

        existing = self.user_repo.get_subscription(self.session, list_id, user_id)
        if not existing:
            self.user_repo.create(
                self.session, ListUser(list_id=list_id, user_id=user_id)
            )
            self._log(
                user_id, group_id, "SUBSCRIBE", f"Subscribed to list {tag_list.name}"
            )
            return True
        return False

    def unsubscribe(
        self, user_id: int, group_id: uuid.UUID, list_id: uuid.UUID
    ) -> bool:
        """
        Unsubscribe a user from a list.

        :param user_id: The ID of the user
        :param group_id: The internal ID of the group
        :param list_id: The internal ID of the list
        :return: True if newly unsubscribed, False if list not found, group ID mismatch, or not subscribed
        """
        self._check_group(group_id)
        tag_list = self.repository.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            return False

        existing = self.user_repo.get_subscription(self.session, list_id, user_id)
        if existing:
            self.user_repo.delete(self.session, existing.id)
            self._log(
                user_id,
                group_id,
                "UNSUBSCRIBE",
                f"Unsubscribed from list {tag_list.name}",
            )
            return True
        return False

    def get_list_members(self, group_id: uuid.UUID, list_id: uuid.UUID) -> list["User"]:
        self._check_group(group_id)
        users_with_details = self.user_repo.get_users_in_list_with_details(
            self.session, list_id
        )
        return [user for list_user, user in users_with_details]

    async def add_member_by_admin(
        self,
        admin_id: int,
        group_id: uuid.UUID,
        list_id: uuid.UUID,
        identifier: str | int,
        bot: Bot | None = None,
    ) -> bool:
        self._check_group(group_id)
        tag_list = self.repository.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            raise ValueError("List not found or group ID mismatch")

        group = self.group_repo.get_by_id(self.session, group_id)

        target_user_id = None

        user_repo_db = UserRepository()

        if isinstance(identifier, str):
            identifier = identifier.lstrip("@")
            user = user_repo_db.get_by_username(self.session, identifier)
            if not user:
                raise ValueError(
                    "User not found in our database. Please provide a valid Telegram ID or ensure they have interacted with the bot."
                )
            target_user_id = user.user_id
        else:
            target_user_id = identifier

        # check if in group

        if not await check_telegram_member(group.telegram_id, target_user_id, bot=bot):
            raise ValueError("User is not a member of the Telegram group.")

        success = self.subscribe(target_user_id, group_id, list_id)
        if success:
            self._log(
                admin_id,
                group_id,
                "ADMIN_ADD_MEMBER",
                f"Admin added user {target_user_id} to list {tag_list.name}",
            )
        return success

    def remove_member_by_admin(
        self,
        admin_id: int,
        group_id: uuid.UUID,
        list_id: uuid.UUID,
        target_user_id: int,
    ) -> bool:
        success = self.unsubscribe(target_user_id, group_id, list_id)
        if success:
            tag_list = self.repository.get_by_id(self.session, list_id)
            list_name = tag_list.name if tag_list else str(list_id)
            self._log(
                admin_id,
                group_id,
                "ADMIN_REMOVE_MEMBER",
                f"Admin removed user {target_user_id} from list {list_name}",
            )
        return success

    async def _apply_tag_rules(
        self,
        list_id: uuid.UUID,
        chat_id: int,
        candidate_user_ids: set[int],
        bot: Bot,
        update: Update | None = None,
    ) -> set[int]:
        """Filter a candidate user set against a list's tag rules.

        Resolves member tags via :class:`MemberTagService`, applies
        ``INCLUDE_ONLY`` (union semantics across multiple rules) and
        ``EXCLUDE`` (set subtraction) modes. AUTO_* modes are no-ops here;
        they are evaluated at tag-change time in
        :meth:`ListRuleService.apply_tag_change`.

        :param list_id: list UUID whose rules govern filtering.
        :param chat_id: telegram chat ID, needed to look up member tags.
        :param candidate_user_ids: raw list membership before filtering.
        :param bot: PTB ``Bot`` for tag resolution on cache miss.
        :param update: optional :class:`Update` to short-circuit lookups.
        :returns: filtered subset of ``candidate_user_ids``.
        """
        if not candidate_user_ids:
            return set()

        rules = await self.rule_service.get_rules_cached(list_id)
        include_values: set[str] = set()
        exclude_values: set[str] = set()
        for r in rules:
            if r["mode"] == ListTagRuleMode.INCLUDE_ONLY.value:
                include_values.add(r["tag_value"])
            elif r["mode"] == ListTagRuleMode.EXCLUDE.value:
                exclude_values.add(r["tag_value"])

        if not include_values and not exclude_values:
            return set(candidate_user_ids)

        tags = await self.member_tag_service.get_tags_bulk(
            bot=bot,
            chat_id=chat_id,
            user_ids=candidate_user_ids,
            update=update,
        )

        if include_values:
            allowed = {uid for uid, tag in tags.items() if tag in include_values}
        else:
            allowed = set(candidate_user_ids)

        excluded = {uid for uid, tag in tags.items() if tag and tag in exclude_values}
        return allowed - excluded

    async def trigger_list_mention(
        self,
        admin_id: int,
        group_id: uuid.UUID,
        list_id: uuid.UUID,
        bot: Bot | None = None,
    ) -> bool:
        self._check_group(group_id)
        tag_list = self.repository.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            raise ValueError("List not found or group ID mismatch")

        group = self.group_repo.get_by_id(self.session, group_id)
        users = self.user_repo.get_users_in_list(self.session, list_id)
        if not users:
            raise ValueError("No one is in the list")

        user_ids = {u.user_id for u in users}

        bot_instance = bot or get_bot()

        user_ids = await self._apply_tag_rules(
            list_id=list_id,
            chat_id=group.telegram_id,
            candidate_user_ids=user_ids,
            bot=bot_instance,
        )
        if not user_ids:
            raise ValueError("No one matches the list's tag rules")

        mentions = await MentionService.build_mentions(
            session=self.session,
            group_id=group_id,
            group_telegram_id=group.telegram_id,
            user_ids=user_ids,
            bot=bot_instance,
        )

        if not mentions:
            raise ValueError("Could not resolve any members")

        # local import: breaks a module-load circular dependency with celery
        # (list_service -> send_telegram_message -> celery_app -> apply_tag_change
        # -> list_service). Importing at call time keeps list_service celery-free.
        from celery_workers.tasks.send_telegram_message import send_telegram_message

        batch_size = 50
        for i in range(0, len(mentions), batch_size):
            batch = mentions[i : i + batch_size]
            message_text = "\n".join(batch) + "\n\n<i>(Triggered by Admin via Web)</i>"

            send_telegram_message.delay(
                chat_id=group.telegram_id,
                text=message_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )

        self._log(
            admin_id,
            group_id,
            "trigger_list_api",
            f"Triggered list {tag_list.name} via API",
        )
        return True

    async def trigger_multiple_lists_by_command(
        self,
        triggering_user_id: int,
        group_id: uuid.UUID,
        list_ids: list[uuid.UUID],
        bot: Bot | None = None,
        update: Update | None = None,
        reply_to_message_id: int | None = None,
    ) -> bool:
        self._check_group(group_id)
        group = self.group_repo.get_by_id(self.session, group_id)

        bot_instance = bot or (update.get_bot() if update else get_bot())

        user_ids: set[int] = set()
        list_names = []
        for list_id in list_ids:
            tag_list = self.repository.get_by_id(self.session, list_id)
            if tag_list:
                list_names.append(tag_list.name)
            users = self.user_repo.get_users_in_list(self.session, list_id)
            candidate = {u.user_id for u in users}
            filtered = await self._apply_tag_rules(
                list_id=list_id,
                chat_id=group.telegram_id,
                candidate_user_ids=candidate,
                bot=bot_instance,
                update=update,
            )
            user_ids.update(filtered)

        if not user_ids:
            raise ValueError("No one is in the list")

        exclude_id = update.effective_user.id if update else None

        mentions = await MentionService.build_mentions(
            session=self.session,
            group_id=group_id,
            group_telegram_id=group.telegram_id,
            user_ids=user_ids,
            exclude_user_id=exclude_id,
            bot=bot_instance,
            update=update,
        )

        if not mentions:
            raise ValueError("Could not resolve any members")

        random_number = random.randint(0, 5)
        donation_text = (
            "\n\nEnjoying this free bot? 🌟 Show your support by making a donation to help keep it running and improving! Every contribution matters. 🙏 Donate here: https://github.com/Matt0550/TagEveryoneTelegramBot#support-me"
            if random_number == 5
            else ""
        )

        # local import: breaks a module-load circular dependency with celery
        # (see trigger_list_by_command above for the full cycle).
        from celery_workers.tasks.send_telegram_message import send_telegram_message

        batch_size = 50
        for i in range(0, len(mentions), batch_size):
            batch = mentions[i : i + batch_size]
            user_mentions = "\n".join(batch)
            if user_mentions:
                message_text = user_mentions + donation_text
                send_telegram_message.delay(
                    chat_id=group.telegram_id,
                    text=message_text,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_to_message_id=reply_to_message_id,
                )

        self._log(
            triggering_user_id,
            group_id,
            "trigger_list",
            f"Message dispatched to lists: {', '.join(list_names)} "
            f"({len(mentions)} users, async)",
        )
        return True
