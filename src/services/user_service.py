from sqlmodel import Session

from models_all.user import User, UserCreate, UserUpdate
from repositories.user_repository import UserRepository


class UserService:
    def __init__(self, session: Session, repository: UserRepository):
        self.session = session
        self.repository = repository

    def get_by_id(self, user_id: int) -> User | None:
        return self.repository.get_by_user_id(self.session, user_id)

    @staticmethod
    def get_or_create_user(session: Session, user_in: UserCreate) -> User:
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
