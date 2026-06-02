from collections.abc import Sequence

from sqlmodel import Session, func, select

from models_all import TagList
from repositories.base_repository import BaseRepository
from utils.pagination import PaginationParams


class ListRepository(BaseRepository[TagList]):
    def __init__(self):
        super().__init__(TagList)

    def get_lists_of_group(self, db: Session, group_id: int, params: PaginationParams) -> tuple[Sequence[TagList], int]:
        statement = select(TagList).where(TagList.group_id == group_id, TagList.active == True)

        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(count_statement).one()

        offset = (params.page - 1) * params.page_size
        statement = statement.offset(offset).limit(params.page_size)

        items = db.exec(statement).all()
        return items, total

    def get_by_trigger_name(self, db: Session, group_id: int, trigger_name: str) -> TagList | None:
        # Note: checking aliases will be done in service or by parsing JSON in SQLite if possible.
        # This just checks the exact trigger_name.
        statement = select(TagList).where(
            TagList.group_id == group_id,
            TagList.trigger_name == trigger_name,
            TagList.active == True
        )
        return db.exec(statement).first()
