from sqlmodel import Session, select

from models_all import GroupAdminExclusion
from repositories.base_repository import BaseRepository


class GroupAdminExclusionRepository(BaseRepository[GroupAdminExclusion]):
    def __init__(self):
        super().__init__(GroupAdminExclusion)

    def is_excluded(self, db: Session, group_id: int, user_id: int) -> bool:
        statement = select(GroupAdminExclusion).where(
            GroupAdminExclusion.group_id == group_id,
            GroupAdminExclusion.user_id == user_id,
            GroupAdminExclusion.active == True
        )
        return db.exec(statement).first() is not None
