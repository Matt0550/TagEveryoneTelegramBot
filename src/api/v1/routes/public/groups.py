import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from api.auth_deps import is_group_admin

from api.auth_deps import require_group_admin
from api.decorators.set_sentry_context import set_sentry_context
from api.dependencies import GroupServiceDep, get_group_service
from api.utils.telegram_auth import TelegramUser, verify_telegram_webapp
from models_all.group import GroupResponse, GroupsResponse, GroupSummaryResponse
from models_all.group_setting import (
    GroupSettingResponse,
    GroupSettingUpdate,
)
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
async def get_groups(
    params: Annotated[PaginationParams, Depends()],
    group_service: Annotated[GroupServiceDep, Depends(get_group_service)],
    user: TelegramUser = Depends(verify_telegram_webapp),
) -> GroupsResponse:
    groups, total = group_service.get_groups_of_user(user.id, params)

    formatted_groups = [GroupSummaryResponse.model_validate(g) for g in groups]

    return GroupsResponse(
        items=formatted_groups,
        count=total,
    )


@router.get(
    "/{group_id}",
    summary="Get a single group for the current user",
    tags=["groups"],
    response_model=GroupResponse,
)
@set_sentry_context
async def get_group(
    group_id: uuid.UUID,
    group_service: Annotated[GroupServiceDep, Depends(get_group_service)],
    list_service: ListServiceDep,
    user: TelegramUser = Depends(verify_telegram_webapp),
) -> GroupResponse:
    group = group_service.repository.get_by_id(group_service.session, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    is_admin = await is_group_admin(group, user, group_service.session)

    # If not admin, check if user is a member of the group
    if not is_admin:
        from api.auth_deps import check_telegram_member

        if not await check_telegram_member(group.telegram_id, user.id):
            raise HTTPException(
                status_code=403, detail="Not authorized to view this group"
            )

    subscribed_list_ids = list_service.get_subscribed_list_ids(user.id)

    response = GroupResponse.model_validate(group)
    response.is_group_admin = is_admin
    response.lists = list_service.format_lists_with_subscriptions(
        group.tag_lists,
        user.id,
        subscribed_list_ids=subscribed_list_ids,
        filter_active=True,
    )

    return response


@router.get(
    "/{group_id}/settings",
    summary="Get group settings",
    tags=["groups"],
    response_model=GroupSettingResponse,
    dependencies=[Depends(require_group_admin)],
)
@set_sentry_context
async def get_group_settings(
    group_id: uuid.UUID,
    group_service: Annotated[GroupServiceDep, Depends(get_group_service)],
) -> GroupSettingResponse:
    try:
        settings = group_service.get_group_settings(group_id)
        data = settings.model_dump()
        data["auto_add_lists"] = settings.auto_add_lists
        return GroupSettingResponse(**data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/{group_id}/settings",
    summary="Update group settings",
    tags=["groups"],
    response_model=GroupSettingResponse,
    dependencies=[Depends(require_group_admin)],
)
@set_sentry_context
async def update_group_settings(
    group_id: uuid.UUID,
    settings_update: GroupSettingUpdate,
    group_service: Annotated[GroupServiceDep, Depends(get_group_service)],
) -> GroupSettingResponse:
    try:
        update_data = settings_update.model_dump(exclude_unset=True)
        updated_settings = group_service.update_group_settings(group_id, update_data)
        data = updated_settings.model_dump()
        data["auto_add_lists"] = updated_settings.auto_add_lists
        return GroupSettingResponse(**data)
    except ValueError as e:
        status_code = 404 if "Group not found" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))
