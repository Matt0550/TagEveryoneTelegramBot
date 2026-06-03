from collections.abc import Sequence

from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from models_all import Group, ListUser, TagList
from repositories.base_repository import BaseRepository
from utils.pagination import PaginationParams


class GroupRepository(BaseRepository[Group]):
    def __init__(self):
        super().__init__(Group)

    def get_by_telegram_id(self, db: Session, telegram_id: int) -> Group | None:
        """
        Get a group by its Telegram ID.

        :param db: The database session
        :param telegram_id: The Telegram ID of the group
        :return: The Group object if found, otherwise None
        """
        return db.exec(select(Group).where(Group.telegram_id == telegram_id)).first()

    def get_groups_of_user(self, db: Session, user_id: int, params: PaginationParams) -> tuple[Sequence[Group], int]:
        """
        Get all active groups that a specific user has active list subscriptions in.

        :param db: The database session
        :param user_id: The ID of the user
        :param params: Pagination parameters
        :return: A tuple containing a sequence of Groups and the total count
        """
        statement = select(Group).join(TagList).join(ListUser).where(
            ListUser.user_id == user_id,
            TagList.active == True,
            Group.active == True
        ).distinct().options(selectinload(Group.tag_lists))

        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(count_statement).one()

        offset = (params.page - 1) * params.page_size
        statement = statement.offset(offset).limit(params.page_size)

        items = db.exec(statement).all()
        return items, total

    def remove_user_from_group(self, db: Session, group_id: int, user_id: int) -> None:
        """
        Remove a user from all lists within a specific group (soft delete their subscriptions).

        :param db: The database session
        :param group_id: The internal ID of the group
        :param user_id: The ID of the user to remove
        """
        statement = select(ListUser).join(TagList).where(
            TagList.group_id == group_id,
            ListUser.user_id == user_id,
            ListUser.active == True
        )
        list_users = db.exec(statement).all()
        for list_user in list_users:
            list_user.active = False
            list_user.deleted_at = func.now()
            db.add(list_user)
        db.commit()
