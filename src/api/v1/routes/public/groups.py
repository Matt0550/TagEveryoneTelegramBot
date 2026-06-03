from typing import Annotated

from fastapi import APIRouter, Depends

from api.decorators.set_sentry_context import set_sentry_context
from api.dependencies import GroupServiceDep, get_group_service
from api.utils.telegram_auth import TelegramUser, verify_telegram_webapp
from models_all.group import GroupResponse, GroupsResponse
from utils.config import settings
from utils.pagination import PaginationParams

router = APIRouter()
from api.dependencies import ListServiceDep


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

    subscribed_list_ids = list_service.get_subscribed_list_ids(user.id)
    admin_results = await group_service.get_admin_statuses(groups, user)

    formatted_groups = []
    for g, is_admin in zip(groups, admin_results, strict=False):
        data = g.model_dump()
        data["is_admin"] = is_admin

        data["lists"] = list_service.format_lists_with_subscriptions(
            g.tag_lists,
            user.id,
            subscribed_list_ids=subscribed_list_ids,
            filter_active=True
        )

        formatted_groups.append(GroupResponse(**data))

    return GroupsResponse(
        items=formatted_groups,
        count=total,
        isOwner=str(user.id) == str(settings.OWNER_ID),
    )
