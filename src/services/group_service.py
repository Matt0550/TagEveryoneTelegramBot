from sqlmodel import Session
from typing import Sequence, Tuple
from models_all import Group
from utils.pagination import PaginationParams
from repositories.group_repository import GroupRepository

class GroupService:
    def __init__(self, session: Session, repository: GroupRepository):
        self.session = session
        self.repository = repository

    def get_groups_of_user(self, user_id: int, params: PaginationParams) -> Tuple[Sequence[Group], int]:
        return self.repository.get_groups_of_user(self.session, user_id, params)

    def remove_user_from_group(self, group_id: int, user_id: int) -> None:
        return self.repository.remove_user_from_group(self.session, group_id, user_id)
