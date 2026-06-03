from collections.abc import Sequence
from datetime import datetime, timedelta

from sqlmodel import Session, func, select

from models_all import Log
from repositories.base_repository import BaseRepository
from utils.pagination import PaginationParams


class LogRepository(BaseRepository[Log]):
    def __init__(self):
        super().__init__(Log)

    def get_weekly_logs(self, db: Session, params: PaginationParams) -> tuple[Sequence[Log], int]:
        """
        Get paginated logs from the past 7 days, ordered by creation date descending.

        :param db: The database session
        :param params: Pagination parameters
        :return: A tuple containing a sequence of Log objects and the total count
        """
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        statement = select(Log).where(Log.created_at >= one_week_ago)

        statement = statement.order_by(Log.created_at.desc())

        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(count_statement).one()

        offset = (params.page - 1) * params.page_size
        statement = statement.offset(offset).limit(params.page_size)

        items = db.exec(statement).all()
        return items, total
