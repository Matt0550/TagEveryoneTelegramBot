from typing import Annotated

from fastapi import APIRouter, Depends

from api.auth_deps import is_group_admin
from api.decorators.set_sentry_context import set_sentry_context
from api.dependencies import GroupServiceDep, get_group_service
from api.utils.telegram_auth import TelegramUser, verify_telegram_webapp
from models_all.group import GroupResponse, GroupsResponse
from utils.config import settings
from utils.pagination import PaginationParams

router = APIRouter()


import asyncio

from api.dependencies import ListServiceDep
from models_all.tag_list import TagListWithSubscriptionResponse


@router.get(
    "",
    summary="Get groups for the current user",
    tags=["groups"],
    response_model=GroupsResponse,
)
@set_sentry_context
async def get_user_groups(
    params: Annotated[PaginationParams, Depends()],
    group_service: Annotated[GroupServiceDep, Depends(get_group_service)],
    list_service: ListServiceDep,
    user: TelegramUser = Depends(verify_telegram_webapp),
) -> GroupsResponse:
    groups, total = group_service.get_groups_of_user(user.id, params)

    user_subs = list_service.user_repo.get_user_subscriptions(list_service.session, user.id)
    subscribed_list_ids = {sub.list_id for sub in user_subs}

    db = group_service.session
    admin_tasks = [is_group_admin(g, user, db) for g in groups]
    admin_results = await asyncio.gather(*admin_tasks)

    formatted_groups = []
    for g, is_admin in zip(groups, admin_results, strict=False):
        data = g.model_dump()
        data["is_admin"] = is_admin

        lists_formatted = []
        for l in g.tag_lists:
            if not l.active:
                continue
            ldata = l.model_dump()
            ldata["is_subscribed"] = l.id in subscribed_list_ids
            lists_formatted.append(TagListWithSubscriptionResponse(**ldata))

        data["lists"] = lists_formatted
        formatted_groups.append(GroupResponse(**data))

    return GroupsResponse(
        items=formatted_groups,
        count=total,
        isOwner=str(user.id) == str(settings.OWNER_ID),
    )








