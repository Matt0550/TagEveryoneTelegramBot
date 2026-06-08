
from sqlmodel import Session, select

from models_all import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_user_id(self, db: Session, user_id: int) -> User | None:
        """
        Get an active user by their Telegram User ID.

        :param db: The database session
        :param user_id: The Telegram user ID
        :return: The User object if found, otherwise None
        """
        statement = select(User).where(User.user_id == user_id, User.active == True)
        return db.exec(statement).first()

    def get_by_username(self, db: Session, username: str) -> User | None:
        """
        Get an active user by their Telegram username.

        :param db: The database session
        :param username: The Telegram username (without @)
        :return: The User object if found, otherwise None
        """
        statement = select(User).where(
            User.username.ilike(username), User.active == True
        )
        return db.exec(statement).first()

    def get_users_by_ids(self, db: Session, user_ids: set[int] | list[int]) -> list[User]:
        """
        Get multiple active users by their Telegram User IDs.

        :param db: The database session
        :param user_ids: An iterable of Telegram user IDs
        :return: A list of User objects
        """
        if not user_ids:
            return []
        statement = select(User).where(User.user_id.in_(user_ids), User.active == True)
        return list(db.exec(statement).all())
