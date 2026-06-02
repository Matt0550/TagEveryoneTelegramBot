import datetime as dt

from sqlmodel import Column, DateTime, Field, func

from models import ModelBase


class LogShared(ModelBase):
    user_id: int | None = Field(default=None)
    group_id: int | None = Field(default=None, foreign_key="groups.id")
    action: str | None = Field(default=None)
    description: str | None = Field(default=None)


class Log(LogShared, table=True):
    __tablename__ = "logs"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    created_at: dt.datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
        default_factory=lambda: dt.datetime.now(dt.UTC),
    )


class LogCreate(LogShared):
    pass


class LogUpdate(LogShared):
    pass


class LogResponse(LogShared):
    id: int
    created_at: dt.datetime


class LogsResponse(ModelBase):
    items: list[LogResponse]
    count: int
