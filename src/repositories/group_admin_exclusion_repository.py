import uuid

from sqlmodel import Session, select

from models_all import GroupAdminExclusion
from repositories.base_repository import BaseRepository


class GroupAdminExclusionRepository(BaseRepository[GroupAdminExclusion]):
    def __init__(self):
        super().__init__(GroupAdminExclusion)

    def is_excluded(self, db: Session, group_id: uuid.UUID, user_id: int) -> bool:
        """
        Check if a user is excluded from admin privileges in a specific group.

        :param db: The database session
        :param group_id: The ID of the group
        :param user_id: The ID of the user
        :return: True if the user is excluded, False otherwise
        """
        statement = select(GroupAdminExclusion).where(
            GroupAdminExclusion.group_id == group_id,
            GroupAdminExclusion.user_id == user_id,
            GroupAdminExclusion.active == True
        )
        return db.exec(statement).first() is not None
