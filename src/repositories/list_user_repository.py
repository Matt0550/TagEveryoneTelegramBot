from sqlmodel import Session, select

from models_all import ListUser
from repositories.base_repository import BaseRepository


class ListUserRepository(BaseRepository[ListUser]):
    def __init__(self):
        super().__init__(ListUser)

    def get_subscription(self, db: Session, list_id: int, user_id: int) -> ListUser | None:
        statement = select(ListUser).where(
            ListUser.list_id == list_id,
            ListUser.user_id == user_id,
            ListUser.active == True
        )
        return db.exec(statement).first()

    def get_users_in_list(self, db: Session, list_id: int) -> list[ListUser]:
        statement = select(ListUser).where(
            ListUser.list_id == list_id,
            ListUser.active == True
        )
        return list(db.exec(statement).all())

    def get_user_subscriptions(self, db: Session, user_id: int) -> list[ListUser]:
        statement = select(ListUser).where(
            ListUser.user_id == user_id,
            ListUser.active == True
        )
        return list(db.exec(statement).all())
