from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from repositories.log_repository import LogRepository
from repositories.user_repository import UserRepository
from services.group_service import GroupService
from services.list_service import ListService
from services.log_service import LogService
from services.user_service import UserService
from utils.session_manager import get_session

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


def get_list_repository() -> ListRepository:
    return ListRepository()


def get_list_user_repository() -> ListUserRepository:
    return ListUserRepository()


GroupServiceDep = Annotated[GroupService, Depends(get_group_service)]


def get_list_service(
    session: SessionDep,
    repository: ListRepoDep,
    user_repo: ListUserRepoDep,
    group_repo: GroupRepoDep,
) -> ListService:
    return ListService(
        session=session,
        repository=repository,
        user_repo=user_repo,
        group_repo=group_repo,
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
LogServiceDep = Annotated[LogService, Depends(get_log_service)]
ListRepoDep = Annotated[ListRepository, Depends(get_list_repository)]
ListUserRepoDep = Annotated[ListUserRepository, Depends(get_list_user_repository)]

ListServiceDep = Annotated[ListService, Depends(get_list_service)]
