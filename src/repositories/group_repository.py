from sqlmodel import Session, select, func
from typing import Sequence, Tuple
from models_all import Group, GroupUser
from repositories.base_repository import BaseRepository
from utils.pagination import PaginationParams

class GroupRepository(BaseRepository[Group]):
    def __init__(self):
        super().__init__(Group)

    def get_groups_of_user(self, db: Session, user_id: int, params: PaginationParams) -> Tuple[Sequence[Group], int]:
        statement = select(Group).join(GroupUser).where(GroupUser.user_id == user_id)
        
        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(count_statement).one()
        
        offset = (params.page - 1) * params.page_size
        statement = statement.offset(offset).limit(params.page_size)
        
        items = db.exec(statement).all()
        return items, total

    def remove_user_from_group(self, db: Session, group_id: int, user_id: int) -> None:
        statement = select(GroupUser).where(GroupUser.group_id == group_id, GroupUser.user_id == user_id)
        group_user = db.exec(statement).first()
        if group_user:
            db.delete(group_user)
            db.commit()
