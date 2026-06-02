from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Column, DateTime, Field, Relationship, func

from models import ModelBase

if TYPE_CHECKING:
    from models_all.group import Group
    from models_all.user import User


class GroupAdminExclusionShared(ModelBase):
    group_id: int = Field(foreign_key="groups.id")
    user_id: int = Field(foreign_key="users.user_id")
    reason: str | None = Field(default=None)


class GroupAdminExclusion(GroupAdminExclusionShared, table=True):
    __tablename__ = "group_admin_exclusions"  # type: ignore

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

    group: Group = Relationship(back_populates="admin_exclusions")
    user: User = Relationship(back_populates="admin_exclusions")


class GroupAdminExclusionCreate(GroupAdminExclusionShared):
    pass


class GroupAdminExclusionUpdate(ModelBase):
    reason: str | None = None
    active: bool | None = None


class GroupAdminExclusionResponse(GroupAdminExclusionShared):
    id: int
    created_at: datetime
    updated_at: datetime | None
    active: bool


class GroupAdminExclusionsResponse(ModelBase):
    items: list[GroupAdminExclusionResponse]
    count: int
