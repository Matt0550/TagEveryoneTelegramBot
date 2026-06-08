import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.auth_deps import (
    TelegramUser,
    require_group_admin,
    require_list_in_group,
)
from api.decorators.set_sentry_context import set_sentry_context
from api.dependencies import (
    ListRuleServiceDep,
    MemberTagServiceDep,
)
from models_all.exceptions import BadRequestException, NotFoundException
from models_all.list_tag_rule import (
    ListTagRuleResponse,
    ListTagRulesBulkUpdate,
    ListTagRulesResponse,
)
from repositories.group_repository import GroupRepository
from utils.session_manager import get_session

router = APIRouter()


@router.get(
    "/groups/{group_id}/lists/{list_id}/rules",
    summary="Get tag rules for a list",
    response_model=ListTagRulesResponse,
    tags=["list-rules"],
)
@set_sentry_context
def get_list_rules(
    group_id: uuid.UUID,
    list_id: uuid.UUID,
    rule_service: ListRuleServiceDep,
    _admin: TelegramUser = Depends(require_group_admin),
    _: None = Depends(require_list_in_group),
) -> ListTagRulesResponse:
    try:
        rules = rule_service.get_rules(group_id, list_id)
    except ValueError as exc:
        raise NotFoundException(str(exc))
    items = [ListTagRuleResponse.model_validate(r) for r in rules]
    return ListTagRulesResponse(items=items, count=len(items))


@router.put(
    "/groups/{group_id}/lists/{list_id}/rules",
    summary="Replace tag rules for a list",
    response_model=ListTagRulesResponse,
    tags=["list-rules"],
)
@set_sentry_context
async def put_list_rules(
    group_id: uuid.UUID,
    list_id: uuid.UUID,
    payload: ListTagRulesBulkUpdate,
    rule_service: ListRuleServiceDep,
    admin: TelegramUser = Depends(require_group_admin),
    _: None = Depends(require_list_in_group),
) -> ListTagRulesResponse:
    try:
        rules = await rule_service.replace_rules(
            admin.id, group_id, list_id, payload.rules
        )
    except ValueError as exc:
        raise BadRequestException(str(exc))
    items = [ListTagRuleResponse.model_validate(r) for r in rules]
    return ListTagRulesResponse(items=items, count=len(items))


@router.delete(
    "/groups/{group_id}/lists/{list_id}/rules/{rule_id}",
    summary="Delete a single tag rule",
    response_model=str,
    tags=["list-rules"],
)
@set_sentry_context
async def delete_list_rule(
    group_id: uuid.UUID,
    list_id: uuid.UUID,
    rule_id: uuid.UUID,
    rule_service: ListRuleServiceDep,
    admin: TelegramUser = Depends(require_group_admin),
    _: None = Depends(require_list_in_group),
) -> str:
    success = await rule_service.delete_rule(admin.id, group_id, rule_id)
    if not success:
        raise NotFoundException("Rule not found")
    return "Rule deleted successfully"


class KnownTagsResponse(BaseModel):
    tags: list[str]


@router.get(
    "/groups/{group_id}/known-tags",
    summary="List Telegram tag values observed in this group",
    response_model=KnownTagsResponse,
    tags=["list-rules"],
)
@set_sentry_context
async def get_known_tags(
    group_id: uuid.UUID,
    member_tag_service: MemberTagServiceDep,
    _admin: TelegramUser = Depends(require_group_admin),
) -> KnownTagsResponse:
    session = next(get_session())
    try:
        group = GroupRepository().get_by_id(session, group_id)
        if not group:
            raise NotFoundException("Group not found")
        tags = await member_tag_service.get_known_tags(group.telegram_id)
    finally:
        session.close()
    return KnownTagsResponse(tags=tags)
