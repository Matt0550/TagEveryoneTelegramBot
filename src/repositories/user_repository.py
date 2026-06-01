from sqlmodel import Session, select
from typing import Optional
from models_all import User
from repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)
        
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[User]:
        statement = select(User).where(User.user_id == user_id)
        return db.exec(statement).first()
