import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.auth_deps import TelegramUser, get_current_user, require_group_admin
from api.decorators.set_sentry_context import set_sentry_context
from api.dependencies import ListServiceDep
from models_all.tag_list import (
    TagListCreate,
    TagListResponse,
    TagListsWithSubscriptionResponse,
    TagListUpdate,
)
from utils.pagination import PaginationParams

router = APIRouter(prefix="/groups/{group_id}/lists", tags=["lists"])


@router.get(
    "",
    summary="Get all lists for a group",
    response_model=TagListsWithSubscriptionResponse,
)
@set_sentry_context
def get_lists(
    group_id: uuid.UUID,
    params: Annotated[PaginationParams, Depends()],
    list_service: ListServiceDep = None,
    user: TelegramUser = Depends(get_current_user),
) -> TagListsWithSubscriptionResponse:
    # Any user can view lists in a group they are inquiring about
    try:
        lists, total = list_service.get_lists(group_id, params)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Format lists with subscription info
    formatted = list_service.format_lists_with_subscriptions(lists, user.id)

    return TagListsWithSubscriptionResponse(items=formatted, count=total)


@router.post(
    "",
    summary="Create a new list",
    response_model=TagListResponse,
)
@set_sentry_context
def create_list(
    group_id: uuid.UUID,
    obj_in: TagListCreate,
    list_service: ListServiceDep = None,
    admin: TelegramUser = Depends(require_group_admin),
) -> TagListResponse:
    if obj_in.group_id != group_id:
        raise HTTPException(status_code=400, detail="Group ID mismatch")

    banned_words = ["start", "help", "admin", "settings", "lists"]
    if obj_in.trigger_name.lower() in banned_words:
        raise HTTPException(status_code=400, detail="Trigger name is not allowed")

    new_list = list_service.create_list(admin.id, obj_in)
    return TagListResponse.model_validate(new_list)


@router.put(
    "/{list_id}",
    summary="Update a list",
    response_model=TagListResponse,
)
@set_sentry_context
def update_list(
    group_id: uuid.UUID,
    list_id: uuid.UUID,
    obj_in: TagListUpdate,
    list_service: ListServiceDep = None,
    admin: TelegramUser = Depends(require_group_admin),
) -> TagListResponse:
    updated = list_service.update_list(admin.id, group_id, list_id, obj_in)
    if not updated:
        raise HTTPException(status_code=404, detail="List not found")
    return TagListResponse.model_validate(updated)


@router.delete(
    "/{list_id}",
    summary="Delete a list",
    response_model=str,
)
@set_sentry_context
def delete_list(
    group_id: uuid.UUID,
    list_id: uuid.UUID,
    list_service: ListServiceDep = None,
    admin: TelegramUser = Depends(require_group_admin),
) -> str:
    try:
        success = list_service.delete_list(admin.id, group_id, list_id)
        if not success:
            raise HTTPException(status_code=404, detail="List not found")
        return "List deleted successfully"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{list_id}/subscribe",
    summary="Subscribe to a list",
    response_model=str,
)
@set_sentry_context
def subscribe_to_list(
    group_id: uuid.UUID,
    list_id: uuid.UUID,
    list_service: ListServiceDep = None,
    user: TelegramUser = Depends(get_current_user),
) -> str:
    try:
        success = list_service.subscribe(user.id, group_id, list_id)
        if not success:
            raise HTTPException(status_code=404, detail="List not found")
        return "Subscribed successfully"
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/{list_id}/unsubscribe",
    summary="Unsubscribe from a list",
    response_model=str,
)
@set_sentry_context
def unsubscribe_from_list(
    group_id: uuid.UUID,
    list_id: uuid.UUID,
    list_service: ListServiceDep = None,
    user: TelegramUser = Depends(get_current_user),
) -> str:
    try:
        success = list_service.unsubscribe(user.id, group_id, list_id)
        if not success:
            raise HTTPException(status_code=404, detail="List not found")
        return "Unsubscribed successfully"
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
