from typing import Annotated

from fastapi import APIRouter, Depends

from api.decorators.set_sentry_context import set_sentry_context
from api.dependencies import LogServiceDep, get_log_service
from api.utils.telegram_auth import TelegramUser, verify_admin
from models_all.log import LogResponse, LogsResponse
from utils.pagination import PaginationParams

router = APIRouter()


@router.get(
    "/logs",
    summary="Get weekly logs (Admin only)",
    tags=["logs"],
    response_model=LogsResponse,
)
@set_sentry_context
def get_admin_logs(
    params: Annotated[PaginationParams, Depends()],
    log_service: Annotated[LogServiceDep, Depends(get_log_service)],
    _user: TelegramUser = Depends(verify_admin),
) -> LogsResponse:
    logs, total = log_service.get_weekly_logs(params)

    formatted_logs = [LogResponse.model_validate(log) for log in logs]

    response_data = LogsResponse(items=formatted_logs, count=total)

    return response_data
