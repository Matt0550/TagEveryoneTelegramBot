from datetime import UTC, datetime
from enum import StrEnum

from sqlmodel import Column, DateTime, Field, Relationship, Text, func

from models import ModelBase


class JobType(StrEnum):
    ANNOUNCE = "announce"


class JobStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AsyncJobShared(ModelBase):
    job_type: str = Field(max_length=50)
    status: str = Field(default=JobStatus.PENDING, max_length=20)
    total_items: int = Field(default=0)
    completed_items: int = Field(default=0)
    failed_items: int = Field(default=0)
    metadata_json: str | None = Field(default=None, sa_column=Column(Text))
    started_by: int  # Telegram user ID of whoever triggered the job
    error_message: str | None = Field(default=None, sa_column=Column(Text))


class AsyncJob(AsyncJobShared, table=True):
    __tablename__ = "async_jobs"  # type: ignore

    id: int = Field(default=None, primary_key=True)

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
        default_factory=lambda: datetime.now(UTC),
    )
    completed_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True),
        default=None,
    )

    # Relationship to announce job groups (only populated for announce jobs)
    announce_groups: list[AnnounceJobGroup] = Relationship(  # noqa: F821
        back_populates="job"
    )


class AsyncJobCreate(AsyncJobShared):
    pass


class AsyncJobResponse(AsyncJobShared):
    id: int
    created_at: datetime
    completed_at: datetime | None


# Avoid circular import — import at module level for type resolution
from models_all.announce_job_group import AnnounceJobGroup  # noqa: E402, F401

AsyncJob.model_rebuild()
