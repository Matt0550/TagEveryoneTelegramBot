import math
from typing import TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(
        default=10, ge=1, le=100, description="Number of items per page"
    )
    sort_by: str | None = Field(default=None, description="Field to sort by")
    sort_desc: bool = Field(default=False, description="Sort in descending order")


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    extra: dict = Field(default_factory=dict)

    @classmethod
    def create(
        cls, items: list[T], total: int, params: PaginationParams, extra: dict = None
    ):
        total_pages = math.ceil(total / params.page_size) if total > 0 else 1
        return cls(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
            extra=extra or {},
        )
