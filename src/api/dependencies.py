from typing import Annotated
from fastapi import Depends
from sqlmodel import Session

from utils.session_manager import get_session

from repositories.group_repository import GroupRepository
from repositories.user_repository import UserRepository
from repositories.log_repository import LogRepository

from services.group_service import GroupService
from services.user_service import UserService
from services.log_service import LogService

SessionDep = Annotated[Session, Depends(get_session)]

def get_group_repository() -> GroupRepository:
    return GroupRepository()

def get_user_repository() -> UserRepository:
    return UserRepository()

def get_log_repository() -> LogRepository:
    return LogRepository()

GroupRepoDep = Annotated[GroupRepository, Depends(get_group_repository)]
UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]
LogRepoDep = Annotated[LogRepository, Depends(get_log_repository)]

def get_group_service(
    session: SessionDep,
    repository: GroupRepoDep,
) -> GroupService:
    return GroupService(session=session, repository=repository)

def get_user_service(
    session: SessionDep,
    repository: UserRepoDep,
) -> UserService:
    return UserService(session=session, repository=repository)

def get_log_service(
    session: SessionDep,
    repository: LogRepoDep,
) -> LogService:
    return LogService(session=session, repository=repository)

GroupServiceDep = Annotated[GroupService, Depends(get_group_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
LogServiceDep = Annotated[LogService, Depends(get_log_service)]
