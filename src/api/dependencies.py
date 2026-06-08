from typing import Annotated

from fastapi import Depends
from sqlmodel import Session
from telegram import Bot

from bot.instance import get_bot as _get_bot_singleton
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_tag_rule_repository import ListTagRuleRepository
from repositories.list_user_repository import ListUserRepository
from repositories.log_repository import LogRepository
from repositories.user_repository import UserRepository
from services.cache_service import CacheService
from services.cache_service import get_cache as _get_cache_singleton
from services.group_service import GroupService
from services.list_rule_service import ListRuleService
from services.list_service import ListService
from services.log_service import LogService
from services.member_tag_service import MemberTagService
from services.user_service import UserService
from utils.session_manager import get_session

SessionDep = Annotated[Session, Depends(get_session)]


def get_bot() -> Bot:
    """FastAPI dependency that returns the shared :class:`telegram.Bot`."""
    return _get_bot_singleton()


def get_cache() -> CacheService:
    """FastAPI dependency that returns the shared :class:`CacheService`."""
    return _get_cache_singleton()


BotDep = Annotated[Bot, Depends(get_bot)]
CacheDep = Annotated[CacheService, Depends(get_cache)]


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
    log_service: LogServiceDep,
    cache: CacheDep,
) -> ListService:
    return ListService(
        session=session,
        repository=repository,
        user_repo=user_repo,
        group_repo=group_repo,
        log_service=log_service,
        cache=cache,
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
LogServiceDep = Annotated[LogService, Depends(get_log_service)]
ListRepoDep = Annotated[ListRepository, Depends(get_list_repository)]
ListUserRepoDep = Annotated[ListUserRepository, Depends(get_list_user_repository)]

ListServiceDep = Annotated[ListService, Depends(get_list_service)]


def get_list_tag_rule_repository() -> ListTagRuleRepository:
    return ListTagRuleRepository()


ListTagRuleRepoDep = Annotated[
    ListTagRuleRepository, Depends(get_list_tag_rule_repository)
]


def get_list_rule_service(
    session: SessionDep,
    repository: ListTagRuleRepoDep,
    list_repo: ListRepoDep,
    group_repo: GroupRepoDep,
    log_service: LogServiceDep,
    cache: CacheDep,
) -> ListRuleService:
    return ListRuleService(
        session=session,
        repository=repository,
        list_repo=list_repo,
        group_repo=group_repo,
        log_service=log_service,
        cache=cache,
    )


ListRuleServiceDep = Annotated[ListRuleService, Depends(get_list_rule_service)]


def get_member_tag_service(cache: CacheDep) -> MemberTagService:
    return MemberTagService(cache=cache)


MemberTagServiceDep = Annotated[MemberTagService, Depends(get_member_tag_service)]
