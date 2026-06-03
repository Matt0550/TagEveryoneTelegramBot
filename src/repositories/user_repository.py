
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
