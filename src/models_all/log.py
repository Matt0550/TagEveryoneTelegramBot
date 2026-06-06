import datetime as dt
import uuid

from sqlalchemy import BigInteger
from sqlmodel import Column, Field, func

from models import ModelBase
from utils.db_types import UTCDateTime


class LogShared(ModelBase):
    user_id: int | None = Field(default=None, sa_column=Column(BigInteger))
    group_id: uuid.UUID | None = Field(default=None, foreign_key="groups.id")
    action: str | None = Field(default=None)
    description: str | None = Field(default=None)


class Log(LogShared, table=True):
    __tablename__ = "logs"  # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)
    created_at: dt.datetime = Field(
        sa_column=Column(
            UTCDateTime(timezone=True), server_default=func.now(), nullable=False
        ),
        default_factory=lambda: dt.datetime.now(dt.UTC),
    )


class LogCreate(LogShared):
    pass


class LogUpdate(LogShared):
    pass


class LogResponse(LogShared):
    id: uuid.UUID
    created_at: dt.datetime


class LogsResponse(ModelBase):
    items: list[LogResponse]
    count: int
