from collections.abc import Sequence

from sqlmodel import Session

from models_all.log import Log, LogCreate
from repositories.log_repository import LogRepository
from utils.pagination import PaginationParams


class LogService:
    def __init__(self, session: Session, repository: LogRepository):
        self.session = session
        self.repository = repository

    def get_weekly_logs(self, params: PaginationParams) -> tuple[Sequence[Log], int]:
        return self.repository.get_weekly_logs(self.session, params)

    @staticmethod
    def add_log(
        session: Session,
        user_id: int,
        group_id: str,
        action: str,
        description: str = None,
    ) -> Log:
        log_create = LogCreate(
            user_id=user_id,
            group_id=int(group_id) if group_id else None,
            action=action,
            description=description,
        )
        log = Log.model_validate(log_create)
        session.add(log)
        session.commit()
        session.refresh(log)
        return log
