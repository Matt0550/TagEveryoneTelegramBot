import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlmodel import Column, Field, Relationship, func

from models import ModelBase
from utils.db_types import UTCDateTime

if TYPE_CHECKING:
    from models_all.group_admin_exclusion import GroupAdminExclusion
    from models_all.list_user import ListUser

class UserShared(ModelBase):
    user_id: int = Field(sa_column=Column(BigInteger, unique=True, nullable=False))
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    username: str | None = Field(default=None)

class User(UserShared, table=True):
    __tablename__ = "users"  # type: ignore

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

    list_memberships: list[ListUser] = Relationship(back_populates="user")
    admin_exclusions: list[GroupAdminExclusion] = Relationship(back_populates="user")


class UserCreate(UserShared):
    pass


class UserUpdate(UserShared):
    pass


class UserResponse(UserShared):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime | None
    active: bool


class UsersResponse(ModelBase):
    items: list[UserResponse]
    count: int
