from sqlmodel import Session, select

from models_all import ListUser
from repositories.base_repository import BaseRepository


class ListUserRepository(BaseRepository[ListUser]):
    def __init__(self):
        super().__init__(ListUser)

    def get_subscription(self, db: Session, list_id: int, user_id: int) -> ListUser | None:
        """
        Get a specific active subscription for a user to a list.

        :param db: The database session
        :param list_id: The ID of the list
        :param user_id: The ID of the user
        :return: The ListUser object if found, otherwise None
        """
        statement = select(ListUser).where(
            ListUser.list_id == list_id,
            ListUser.user_id == user_id,
            ListUser.active == True
        )
        return db.exec(statement).first()

    def get_users_in_list(self, db: Session, list_id: int) -> list[ListUser]:
        """
        Get all active user subscriptions for a specific list.

        :param db: The database session
        :param list_id: The ID of the list
        :return: A list of ListUser objects
        """
        statement = select(ListUser).where(
            ListUser.list_id == list_id,
            ListUser.active == True
        )
        return list(db.exec(statement).all())

    def get_user_subscriptions(self, db: Session, user_id: int) -> list[ListUser]:
        """
        Get all active list subscriptions for a specific user.

        :param db: The database session
        :param user_id: The ID of the user
        :return: A list of ListUser objects representing the user's subscriptions
        """
        statement = select(ListUser).where(
            ListUser.user_id == user_id,
            ListUser.active == True
        )
        return list(db.exec(statement).all())
