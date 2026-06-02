from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import JSON, Column, DateTime, Field, Relationship, func

from models import ModelBase

if TYPE_CHECKING:
    from models_all.group import Group
    from models_all.list_user import ListUser


class TagListShared(ModelBase):
    group_id: int = Field(foreign_key="groups.id")
    name: str
    description: str | None = Field(default=None)
    trigger_name: str
    is_system: bool = Field(default=False)
    aliases: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class TagList(TagListShared, table=True):
    __tablename__ = "tag_lists"  # type: ignore

    id: int = Field(default=None, primary_key=True)

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
        default_factory=lambda: datetime.now(UTC),
    )
    updated_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True),
        default=None,
    )
    deleted_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True), default=None
    )
    active: bool = Field(default=True, nullable=False)

    group: Group = Relationship(back_populates="tag_lists")
    list_users: list[ListUser] = Relationship(back_populates="tag_list", cascade_delete=True)


class TagListCreate(TagListShared):
    pass


class TagListUpdate(ModelBase):
    name: str | None = None
    description: str | None = None
    trigger_name: str | None = None
    aliases: list[str] | None = None
    active: bool | None = None


class TagListResponse(TagListShared):
    id: int
    created_at: datetime
    updated_at: datetime | None
    active: bool


class TagListsResponse(ModelBase):
    items: list[TagListResponse]
    count: int

class TagListWithSubscriptionResponse(TagListResponse):
    is_subscribed: bool

class TagListsWithSubscriptionResponse(ModelBase):
    items: list[TagListWithSubscriptionResponse]
    count: int
