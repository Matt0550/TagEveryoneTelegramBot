import datetime as dt

from sqlalchemy.types import DateTime, TypeDecorator


class UTCDateTime(TypeDecorator):
    """
    A custom SQLAlchemy type that ensures datetime objects are always timezone-aware (UTC)
    when reading from and writing to the database. This fixes issues with SQLite returning
    offset-naive datetimes.
    """
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                value = value.replace(tzinfo=dt.UTC)
            return value.astimezone(dt.UTC)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                return value.replace(tzinfo=dt.UTC)
            return value.astimezone(dt.UTC)
        return value
