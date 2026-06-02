from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from models import ModelBase

if TYPE_CHECKING:
    from models_all.group_admin_exclusion import GroupAdminExclusion
    from models_all.tag_list import TagList


class GroupShared(ModelBase):
    telegram_id: int = Field(sa_column_kwargs={"unique": True})
    group_name: str | None = Field(default=None)
    group_description: str | None = Field(default=None)
    group_username: str | None = Field(default=None)
    group_type: str | None = Field(default=None)
    group_members: int | None = Field(default=None)


from sqlmodel import Column, DateTime, func


class Group(GroupShared, table=True):
    __tablename__ = "groups"  # type: ignore
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

    tag_lists: list[TagList] = Relationship(back_populates="group")
    admin_exclusions: list[GroupAdminExclusion] = Relationship(back_populates="group")


class GroupCreate(GroupShared):
    pass


class GroupUpdate(GroupShared):
    pass


from models_all.tag_list import TagListWithSubscriptionResponse


class GroupResponse(GroupShared):
    id: int
    active: bool
    is_admin: bool = False
    lists: list[TagListWithSubscriptionResponse] = []


class GroupsResponse(ModelBase):
    items: list[GroupResponse]
    count: int
    isOwner: bool | None = False
