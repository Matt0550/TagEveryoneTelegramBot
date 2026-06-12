import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Column, Field, Relationship, func

from models import ModelBase
from models_all.group_setting_tag_list_link import GroupSettingTagListLink
from utils.db_types import UTCDateTime

if TYPE_CHECKING:
    from models_all.group import Group
    from models_all.tag_list import TagList


class GroupSettingShared(ModelBase):
    group_id: uuid.UUID = Field(foreign_key="groups.id", unique=True)
    auto_add_new_members: bool = Field(default=False)
    # Language the bot replies in for this group (ISO 639-1). English default.
    language: str = Field(default="en", max_length=8)


class GroupSetting(GroupSettingShared, table=True):
    __tablename__ = "group_settings"  # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)

    created_at: datetime = Field(
        sa_column=Column(
            UTCDateTime(timezone=True), server_default=func.now(), nullable=False
        ),
        default_factory=lambda: datetime.now(UTC),
    )
    updated_at: datetime | None = Field(
        sa_column=Column(
            UTCDateTime(timezone=True), onupdate=func.now(), nullable=True
        ),
        default=None,
    )
    deleted_at: datetime | None = Field(
        sa_column=Column(UTCDateTime(timezone=True), nullable=True), default=None
    )
    active: bool = Field(default=True, nullable=False)

    group: "Group" = Relationship(back_populates="settings")
    auto_add_lists: list["TagList"] = Relationship(
        link_model=GroupSettingTagListLink,
        sa_relationship_kwargs={
            "primaryjoin": "and_(GroupSetting.id==GroupSettingTagListLink.group_setting_id, GroupSettingTagListLink.active==True)",
            "secondaryjoin": "and_(TagList.id==GroupSettingTagListLink.tag_list_id, TagList.active==True)",
        },
    )


class GroupSettingCreate(GroupSettingShared):
    auto_add_list_ids: list[uuid.UUID] | None = None


class GroupSettingUpdate(ModelBase):
    auto_add_new_members: bool | None = None
    auto_add_list_ids: list[uuid.UUID] | None = None
    language: str | None = None


from models_all.tag_list import TagListResponse


class GroupSettingResponse(GroupSettingShared):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None
    active: bool
    auto_add_list_ids: list[TagListResponse] = Field(
        default_factory=list, alias="auto_add_lists"
    )
