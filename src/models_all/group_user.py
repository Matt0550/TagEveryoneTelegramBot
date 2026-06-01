import datetime as dt
from typing import TYPE_CHECKING

from sqlmodel import Column, DateTime, Field, Relationship, func
from models import ModelBase

if TYPE_CHECKING:
    from models_all.group import Group
    from models_all.user import User


class GroupUserShared(ModelBase):
    group_id: int = Field(foreign_key="groups.group_id")
    user_id: int = Field(foreign_key="users.user_id")


class GroupUser(GroupUserShared, table=True):
    __tablename__ = "groups_users"  # type: ignore
    
    id: int = Field(default=None, primary_key=True)
    datetime: dt.datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
        default_factory=lambda: dt.datetime.now(dt.UTC),
    )
    
    group: "Group" = Relationship(back_populates="user_memberships")
    user: "User" = Relationship(back_populates="group_memberships")


class GroupUserCreate(GroupUserShared):
    pass


class GroupUserUpdate(GroupUserShared):
    pass


class GroupUserResponse(GroupUserShared):
    id: int
    datetime: dt.datetime


class GroupUsersResponse(ModelBase):
    items: list[GroupUserResponse]
    count: int
