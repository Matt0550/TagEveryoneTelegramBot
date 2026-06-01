from api.dependencies import get_group_service
from typing import Annotated
from models_all.group import GroupsResponse, GroupResponse
from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import GroupServiceDep
from api.utils.telegram_auth import verify_telegram_webapp, TelegramUser
from api.decorators.set_sentry_context import set_sentry_context
from utils.config import settings
from models import GenericResponse
from utils.pagination import PaginationParams

router = APIRouter()


@router.get(
    "",
    summary="Get groups for the current user",
    tags=["groups"],
    response_model=GroupsResponse,
)
@set_sentry_context
def get_user_groups(
    params: Annotated[PaginationParams, Depends()],
    group_service: Annotated[GroupServiceDep, Depends(get_group_service)],
    user: TelegramUser = Depends(verify_telegram_webapp),
) -> GroupsResponse:
    print(user)
    groups, total = group_service.get_groups_of_user(user.id, params)

    formatted_groups = [GroupResponse.model_validate(g) for g in groups]
    print(formatted_groups)

    return GroupsResponse(
        items=formatted_groups,
        count=total,
        isOwner=str(user.id) == str(settings.OWNER_ID),
    )


@router.post(
    "/{group_id}/leave", summary="Leave a group", response_model=GenericResponse[dict]
)
@set_sentry_context
def leave_group(
    group_id: int,
    group_service: Annotated[GroupServiceDep, Depends(get_group_service)],
    user: TelegramUser = Depends(verify_telegram_webapp),
):
    try:
        group_service.remove_user_from_group(group_id, user.id)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return GenericResponse(
        message={"message": "Successfully removed from tag list!"}, status_code=200
    )
