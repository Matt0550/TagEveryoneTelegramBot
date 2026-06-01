from sqlmodel import Session
from typing import Sequence, Tuple
from models_all import Log
from utils.pagination import PaginationParams
from repositories.log_repository import LogRepository

class LogService:
    def __init__(self, session: Session, repository: LogRepository):
        self.session = session
        self.repository = repository

    def get_weekly_logs(self, params: PaginationParams) -> Tuple[Sequence[Log], int]:
        return self.repository.get_weekly_logs(self.session, params)
