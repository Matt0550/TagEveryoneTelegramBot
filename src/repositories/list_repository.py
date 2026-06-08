import uuid
from collections.abc import Sequence

from sqlmodel import Session, func, select

from models_all import TagList
from repositories.base_repository import BaseRepository
from utils.pagination import PaginationParams


class ListRepository(BaseRepository[TagList]):
    def __init__(self):
        super().__init__(TagList)

    def get_lists_of_group(self, db: Session, group_id: uuid.UUID, params: PaginationParams) -> tuple[Sequence[TagList], int]:
        """
        Get all active paginated lists within a specific group.

        :param db: The database session
        :param group_id: The ID of the group
        :param params: Pagination parameters
        :return: A tuple containing a sequence of TagList objects and the total count
        """
        statement = select(TagList).where(TagList.group_id == group_id, TagList.active == True)

        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(count_statement).one()

        offset = (params.page - 1) * params.page_size
        statement = statement.offset(offset).limit(params.page_size)

        items = db.exec(statement).all()
        return items, total

    def get_active_for_group(self, db: Session, group_id: uuid.UUID) -> Sequence[TagList]:
        """Return every active list belonging to a group, no pagination.

        :param db: database session.
        :param group_id: internal UUID of the group.
        :returns: sequence of active :class:`TagList` rows for the group.
        """
        statement = select(TagList).where(
            TagList.group_id == group_id, TagList.active == True
        )
        return db.exec(statement).all()

    def get_by_trigger_name(self, db: Session, group_id: uuid.UUID, trigger_name: str) -> TagList | None:
        """
        Get an active list in a specific group by its trigger name.
        Note: checking aliases will be done in service or by parsing JSON in SQLite if possible.
        This just checks the exact trigger_name.

        :param db: The database session
        :param group_id: The ID of the group
        :param trigger_name: The trigger name to search for
        :return: The TagList object if found, otherwise None
        """
        statement = select(TagList).where(
            TagList.group_id == group_id,
            TagList.trigger_name == trigger_name,
            TagList.active == True
        )
        return db.exec(statement).first()
