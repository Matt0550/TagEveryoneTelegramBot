import uuid
from collections.abc import Sequence

from sqlmodel import Session

from models_all.log import Log, LogCreate
from repositories.group_repository import GroupRepository
from repositories.log_repository import LogRepository
from utils.pagination import PaginationParams


class LogService:
    def __init__(self, session: Session, repository: LogRepository):
        self.session = session
        self.repository = repository

    def get_weekly_logs(self, params: PaginationParams) -> tuple[Sequence[Log], int]:
        """
        Get logs from the past 7 days, paginated.

        :param params: Pagination parameters
        :return: A tuple containing a sequence of Log objects and the total count
        """
        return self.repository.get_weekly_logs(self.session, params)

    @staticmethod
    def add_log(
        session: Session,
        user_id: int,
        group_id: uuid.UUID | int | str | None,
        action: str,
        description: str = None,
    ) -> Log:
        """
        Create a new log entry.

        :param session: The database session
        :param user_id: The ID of the user performing the action
        :param group_id: The ID of the group where the action occurred
        :param action: A string representing the action type
        :param description: An optional human-readable description
        :return: The created Log object
        """
        real_group_id = None
        if group_id:
            if isinstance(group_id, uuid.UUID):
                real_group_id = group_id
            else:
                try:
                    # Check if it's a UUID string
                    real_group_id = uuid.UUID(str(group_id))
                except ValueError:
                    # It's likely a Telegram ID
                    try:
                        group = GroupRepository().get_by_telegram_id(
                            session, int(group_id)
                        )
                        if group:
                            real_group_id = group.id
                    except (ValueError, TypeError):
                        pass

        log_create = LogCreate(
            user_id=user_id,
            group_id=real_group_id,
            action=action.upper(),
            description=description,
        )
        log = Log.model_validate(log_create)
        session.add(log)
        session.commit()
        session.refresh(log)
        return log
