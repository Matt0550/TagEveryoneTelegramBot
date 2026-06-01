from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship
from models import ModelBase

if TYPE_CHECKING:
    from models_all.group_user import GroupUser


class GroupShared(ModelBase):
    group_id: int = Field(sa_column_kwargs={"unique": True})
    group_name: str | None = Field(default=None)
    group_description: str | None = Field(default=None)
    group_username: str | None = Field(default=None)
    group_type: str | None = Field(default=None)
    group_members: int | None = Field(default=None)


class Group(GroupShared, table=True):
    __tablename__ = "groups"  # type: ignore
    id: int = Field(default=None, primary_key=True)
    
    user_memberships: list["GroupUser"] = Relationship(back_populates="group")


class GroupCreate(GroupShared):
    pass


class GroupUpdate(GroupShared):
    pass


class GroupResponse(GroupShared):
    id: int


class GroupsResponse(ModelBase):
    items: list[GroupResponse]
    count: int
    isOwner: bool | None = False
