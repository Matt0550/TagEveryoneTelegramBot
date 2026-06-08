
from sqlmodel import Session

from models_all.user import User, UserCreate, UserUpdate
from repositories.user_repository import UserRepository
from services.base_service import BaseService
from services.cache_service import CacheService
from services.log_service import LogService


class UserService(BaseService):
    def __init__(
        self,
        session: Session,
        repository: UserRepository,
        log_service: LogService | None = None,
        cache: CacheService | None = None,
    ):
        """:param session: SQLModel session.
        :param repository: :class:`UserRepository` for user access.
        :param log_service: optional audit log writer.
        :param cache: optional cache service.
        """
        super().__init__(session=session, log_service=log_service, cache=cache)
        self.repository = repository

    def get_by_id(self, user_id: int) -> User | None:
        """
        Get a user by their Telegram User ID.

        :param user_id: The Telegram user ID
        :return: The User object if found, otherwise None
        """
        return self.repository.get_by_user_id(self.session, user_id)

    @staticmethod
    def get_or_create_user(session: Session, user_in: UserCreate) -> User:
        """
        Get a user by ID or create one if they don't exist.
        Updates user info (username, first_name, last_name) if changed.

        :param session: The database session
        :param user_in: The UserCreate schema with user details
        :return: The existing or newly created User object
        """
        user_repo = UserRepository()
        user = user_repo.get_by_user_id(session, user_in.user_id)
        if not user:
            user = User.model_validate(user_in)
            user_repo.create(session, user)
        else:
            if (
                user.username != user_in.username
                or user.first_name != user_in.first_name
                or user.last_name != user_in.last_name
            ):
                user_update = UserUpdate(
                    username=user_in.username,
                    first_name=user_in.first_name,
                    last_name=user_in.last_name,
                )
                user_repo.update(
                    session, user, user_update.model_dump(exclude_unset=True)
                )
        return user

    def get_users_by_ids(self, user_ids: set[int] | list[int]) -> list[User]:
        """
        Get multiple active users by their Telegram User IDs.

        :param user_ids: An iterable of Telegram user IDs
        :return: A list of User objects
        """
        return self.repository.get_users_by_ids(self.session, user_ids)
