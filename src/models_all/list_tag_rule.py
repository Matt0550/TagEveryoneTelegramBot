import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlmodel import Column, Field, Relationship, func

from models import ModelBase
from utils.db_types import UTCDateTime

if TYPE_CHECKING:
    from models_all.tag_list import TagList


class ListTagRuleMode(str, Enum):
    EXCLUDE = "EXCLUDE"
    INCLUDE_ONLY = "INCLUDE_ONLY"
    AUTO_ADD = "AUTO_ADD"
    AUTO_REMOVE = "AUTO_REMOVE"


class ListTagRuleShared(ModelBase):
    list_id: uuid.UUID = Field(foreign_key="tag_lists.id")
    tag_value: str = Field(index=True)
    mode: ListTagRuleMode = Field(
        sa_column=Column(SAEnum(ListTagRuleMode), nullable=False)
    )


class ListTagRule(ListTagRuleShared, table=True):
    __tablename__ = "list_tag_rules"  # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)

    created_at: datetime = Field(
        sa_column=Column(
            UTCDateTime(timezone=True), server_default=func.now(), nullable=False
        ),
        default_factory=lambda: datetime.now(UTC),
    )
    updated_at: datetime | None = Field(
        sa_column=Column(UTCDateTime(timezone=True), onupdate=func.now(), nullable=True),
        default=None,
    )
    deleted_at: datetime | None = Field(
        sa_column=Column(UTCDateTime(timezone=True), nullable=True), default=None
    )
    active: bool = Field(default=True, nullable=False)

    tag_list: "TagList" = Relationship(back_populates="tag_rules")


class ListTagRuleCreate(ListTagRuleShared):
    pass


class ListTagRuleUpdate(ModelBase):
    tag_value: str | None = None
    mode: ListTagRuleMode | None = None
    active: bool | None = None


class ListTagRuleResponse(ListTagRuleShared):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime | None
    active: bool


class ListTagRulesResponse(ModelBase):
    items: list[ListTagRuleResponse]
    count: int


class ListTagRuleItem(ModelBase):
    """Single rule entry used in bulk PUT payloads."""

    tag_value: str
    mode: ListTagRuleMode


class ListTagRulesBulkUpdate(ModelBase):
    rules: list[ListTagRuleItem]
