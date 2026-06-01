from sqlmodel import Session
from typing import Optional
from models_all import User
from repositories.user_repository import UserRepository

class UserService:
    def __init__(self, session: Session, repository: UserRepository):
        self.session = session
        self.repository = repository

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.repository.get_by_user_id(self.session, user_id)
