
from sqlmodel import Session

from models_all import ListUser, Log, TagList, TagListCreate, TagListUpdate
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository


from repositories.group_repository import GroupRepository
from utils.pagination import PaginationParams
from typing import Sequence

class ListService:
    def __init__(self, session: Session, repository: ListRepository, user_repo: ListUserRepository, group_repo: GroupRepository):
        self.session = session
        self.repository = repository
        self.user_repo = user_repo
        self.group_repo = group_repo

    def _check_group(self, group_id: int):
        if not self.group_repo.get_by_id(self.session, group_id):
            raise ValueError("Group not found")

    def get_lists(self, group_id: int, params: PaginationParams) -> tuple[Sequence[TagList], int]:
        self._check_group(group_id)
        return self.repository.get_lists_of_group(self.session, group_id, params)

    def create_list(self, user_id: int, obj_in: TagListCreate) -> TagList:
        self._check_group(obj_in.group_id)
        new_list = self.repository.create(self.session, TagList(**obj_in.model_dump()))
        self._log(user_id, obj_in.group_id, "CREATE_LIST", f"Created list {obj_in.name}")
        return new_list

    def update_list(self, user_id: int, group_id: int, list_id: int, obj_in: TagListUpdate) -> TagList | None:
        self._check_group(group_id)
        tag_list = self.repository.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            return None
        updated = self.repository.update(self.session, tag_list, obj_in.model_dump(exclude_unset=True))
        self._log(user_id, group_id, "UPDATE_LIST", f"Updated list {updated.name}")
        return updated

    def delete_list(self, user_id: int, group_id: int, list_id: int) -> bool:
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

    def subscribe(self, user_id: int, group_id: int, list_id: int) -> bool:
        self._check_group(group_id)
        tag_list = self.repository.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            return False

        existing = self.user_repo.get_subscription(self.session, list_id, user_id)
        if not existing:
            self.user_repo.create(self.session, ListUser(list_id=list_id, user_id=user_id))
            self._log(user_id, group_id, "SUBSCRIBE", f"Subscribed to list {tag_list.name}")
        return True

    def unsubscribe(self, user_id: int, group_id: int, list_id: int) -> bool:
        self._check_group(group_id)
        tag_list = self.repository.get_by_id(self.session, list_id)
        if not tag_list or tag_list.group_id != group_id:
            return False

        existing = self.user_repo.get_subscription(self.session, list_id, user_id)
        if existing:
            self.user_repo.delete(self.session, existing.id)
            self._log(user_id, group_id, "UNSUBSCRIBE", f"Unsubscribed from list {tag_list.name}")
        return True

    def _log(self, user_id: int, group_id: int, action: str, description: str):
        log = Log(user_id=user_id, group_id=group_id, action=action, description=description)
        self.session.add(log)
        self.session.commit()
