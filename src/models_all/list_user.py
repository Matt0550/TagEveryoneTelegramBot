import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey
from sqlmodel import Column, DateTime, Field, Relationship, func

from models import ModelBase

if TYPE_CHECKING:
    from models_all.tag_list import TagList
    from models_all.user import User


class ListUserShared(ModelBase):
    list_id: uuid.UUID = Field(foreign_key="tag_lists.id")
    user_id: int = Field(sa_column=Column(BigInteger, ForeignKey("users.user_id"), nullable=False))


class ListUser(ListUserShared, table=True):
    __tablename__ = "list_users"  # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)

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

    tag_list: TagList = Relationship(back_populates="list_users")
    user: User = Relationship(back_populates="list_memberships")


class ListUserCreate(ListUserShared):
    pass


class ListUserUpdate(ModelBase):
    active: bool | None = None


class ListUserResponse(ListUserShared):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime | None
    active: bool


class ListUsersResponse(ModelBase):
    items: list[ListUserResponse]
    count: int
