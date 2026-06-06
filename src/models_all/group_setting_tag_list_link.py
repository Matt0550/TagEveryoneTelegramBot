import uuid
from datetime import UTC, datetime

from sqlmodel import Column, Field, SQLModel, func

from utils.db_types import UTCDateTime


class GroupSettingTagListLink(SQLModel, table=True):
    __tablename__ = "group_setting_tag_list_links"  # type: ignore

    group_setting_id: uuid.UUID = Field(
        foreign_key="group_settings.id", primary_key=True
    )
    tag_list_id: uuid.UUID = Field(
        foreign_key="tag_lists.id", primary_key=True
    )
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

