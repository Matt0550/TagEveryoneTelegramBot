from sqlmodel import Session, select, func
from typing import Sequence, Tuple
from datetime import datetime, timedelta
from models_all import Log
from repositories.base_repository import BaseRepository
from utils.pagination import PaginationParams

class LogRepository(BaseRepository[Log]):
    def __init__(self):
        super().__init__(Log)

    def get_weekly_logs(self, db: Session, params: PaginationParams) -> Tuple[Sequence[Log], int]:
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        statement = select(Log).where(Log.datetime >= one_week_ago)
        
        statement = statement.order_by(Log.datetime.desc())
        
        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(count_statement).one()
        
        offset = (params.page - 1) * params.page_size
        statement = statement.offset(offset).limit(params.page_size)
        
        items = db.exec(statement).all()
        return items, total
