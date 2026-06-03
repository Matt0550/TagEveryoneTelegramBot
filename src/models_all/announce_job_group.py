from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlmodel import Column, DateTime, Field, Relationship, Text, func

from models import ModelBase

if TYPE_CHECKING:
    from models_all.async_job import AsyncJob


class AnnounceGroupStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class AnnounceJobGroupShared(ModelBase):
    job_id: int = Field(foreign_key="async_jobs.id")
    group_telegram_id: int
    group_name: str | None = Field(default=None)
    status: str = Field(default=AnnounceGroupStatus.PENDING, max_length=20)
    error_message: str | None = Field(default=None, sa_column=Column(Text))


class AnnounceJobGroup(AnnounceJobGroupShared, table=True):
    __tablename__ = "announce_job_groups"  # type: ignore

    id: int = Field(default=None, primary_key=True)

    sent_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True),
        default=None,
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
        default_factory=lambda: datetime.now(UTC),
    )

    job: AsyncJob = Relationship(back_populates="announce_groups")


class AnnounceJobGroupCreate(AnnounceJobGroupShared):
    pass


class AnnounceJobGroupResponse(AnnounceJobGroupShared):
    id: int
    sent_at: datetime | None
    created_at: datetime
