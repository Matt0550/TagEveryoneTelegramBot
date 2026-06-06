
import uuid
from collections.abc import Sequence

from sqlmodel import Session

from models_all import ListUser, Log, TagList, TagListCreate, TagListUpdate
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from utils.pagination import PaginationParams


class ListService:
    def __init__(self, session: Session, repository: ListRepository, user_repo: ListUserRepository, group_repo: GroupRepository):
        self.session = session
        self.repository = repository
        self.user_repo = user_repo
        self.group_repo = group_repo

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
        filter_active: bool = False
    ) -> list:
        """
        Format TagList objects to include subscription status for a specific user.

        :param lists: The sequence of TagList objects to format
        :param user_id: The ID of the user
        :param subscribed_list_ids: An optional pre-fetched set of list IDs the user is subscribed to
        :param filter_active: If True, exclude inactive lists
        :return: A list of TagListWithSubscriptionResponse objects (as dicts or models)
        """
        from models_all.tag_list import TagListWithSubscriptionResponse

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

    def get_lists(self, group_id: uuid.UUID, params: PaginationParams) -> tuple[Sequence[TagList], int]:
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
        self._log(user_id, obj_in.group_id, "CREATE_LIST", f"Created list {obj_in.name}")
        return new_list

    def update_list(self, user_id: int, group_id: uuid.UUID, list_id: uuid.UUID, obj_in: TagListUpdate) -> TagList | None:
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
        updated = self.repository.update(self.session, tag_list, obj_in.model_dump(exclude_unset=True))
        self._log(user_id, group_id, "UPDATE_LIST", f"Updated list {updated.name}")
        return updated

    def delete_list(self, user_id: int, group_id: uuid.UUID, list_id: uuid.UUID) -> bool:
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

        success = self.repository.delete(self.session, list_id)
        if success:
            self._log(user_id, group_id, "DELETE_LIST", f"Deleted list {tag_list.name}")
        return success

    def clear_list(self, user_id: int, group_id: uuid.UUID, list_id: uuid.UUID) -> bool:
        """
        Clear all users from a list.

        :param user_id: The ID of the user clearing the list
        :param group_id: The internal ID of the group
        :param list_id: The internal ID of the list
        :return: True if successfully cleared, False if not found or group ID mismatch
        """
        self._check_group(group_id)
        tag_list = self.repository.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            return False

        cleared_count = self.user_repo.clear_list_subscriptions(self.session, list_id)
        self.session.commit()
        self._log(user_id, group_id, "CLEAR_LIST", f"Cleared {cleared_count} users from list {tag_list.name}")
        return True

    def subscribe(self, user_id: int, group_id: uuid.UUID, list_id: uuid.UUID) -> bool:
        """
        Subscribe a user to a list.

        :param user_id: The ID of the user
        :param group_id: The internal ID of the group
        :param list_id: The internal ID of the list
        :return: True if successfully subscribed or already subscribed, False if list not found or group ID mismatch
        """
        self._check_group(group_id)
        tag_list = self.repository.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            return False

        existing = self.user_repo.get_subscription(self.session, list_id, user_id)
        if not existing:
            self.user_repo.create(self.session, ListUser(list_id=list_id, user_id=user_id))
            self._log(user_id, group_id, "SUBSCRIBE", f"Subscribed to list {tag_list.name}")
        return True

    def unsubscribe(self, user_id: int, group_id: uuid.UUID, list_id: uuid.UUID) -> bool:
        """
        Unsubscribe a user from a list.

        :param user_id: The ID of the user
        :param group_id: The internal ID of the group
        :param list_id: The internal ID of the list
        :return: True if successfully unsubscribed or not subscribed, False if list not found or group ID mismatch
        """
        self._check_group(group_id)
        tag_list = self.repository.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            return False

        existing = self.user_repo.get_subscription(self.session, list_id, user_id)
        if existing:
            self.user_repo.delete(self.session, existing.id)
            self._log(user_id, group_id, "UNSUBSCRIBE", f"Unsubscribed from list {tag_list.name}")
        return True

    def _log(self, user_id: int, group_id: uuid.UUID, action: str, description: str):
        """
        Log an action performed by a user in a group.

        :param user_id: The ID of the user performing the action
        :param group_id: The ID of the group where the action occurred
        :param action: A short string identifying the action type
        :param description: A human-readable description of the action
        """
        log = Log(user_id=user_id, group_id=group_id, action=action, description=description)
        self.session.add(log)
        self.session.commit()
