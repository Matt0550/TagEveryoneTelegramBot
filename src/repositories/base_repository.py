from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, TypeVar

from sqlmodel import Session, SQLModel, func, select, update

from utils.pagination import PaginationParams

T = TypeVar("T", bound=SQLModel)


class BaseRepository[T: SQLModel]:
    def __init__(self, model: type[T]):
        self.model = model

    def get_by_id(self, db: Session, id: Any) -> T | None:
        """
        Get an entity by its ID.

        :param db: The database session
        :param id: The ID of the entity
        :return: The entity if found and active, otherwise None
        """
        obj = db.get(self.model, id)
        if obj and hasattr(obj, "active") and not obj.active:
            return None
        return obj

    def get_all(
        self, db: Session, params: PaginationParams, filters: dict[str, Any] = None
    ) -> tuple[Sequence[T], int]:
        """
        Get all entities, with pagination and optional filtering.

        :param db: The database session
        :param params: Pagination parameters (page, page_size, sort_by, sort_desc)
        :param filters: Optional dictionary of column filters
        :return: A tuple containing a sequence of entities and the total count
        """
        statement = select(self.model)

        if hasattr(self.model, "active"):
            statement = statement.where(self.model.active == True)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    statement = statement.where(getattr(self.model, key) == value)

        # Total count
        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(count_statement).one()

        # Sorting
        if params.sort_by and hasattr(self.model, params.sort_by):
            column = getattr(self.model, params.sort_by)
            if params.sort_desc:
                statement = statement.order_by(column.desc())
            else:
                statement = statement.order_by(column.asc())

        # Pagination
        offset = (params.page - 1) * params.page_size
        statement = statement.offset(offset).limit(params.page_size)

        items = db.exec(statement).all()
        return items, total

    def create(self, db: Session, obj_in: T) -> T:
        """
        Create a new entity in the database.

        :param db: The database session
        :param obj_in: The entity to create
        :return: The created entity
        """
        db.add(obj_in)
        db.commit()
        db.refresh(obj_in)
        return obj_in

    def update(self, db: Session, db_obj: T, obj_in: dict[str, Any]) -> T:
        """
        Update an existing entity in the database.

        :param db: The database session
        :param db_obj: The existing database object to update
        :param obj_in: A dictionary of new values
        :return: The updated entity
        """
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete_where(self, db: Session, *conditions: Any) -> int:
        """Bulk soft-delete rows matching the given conditions in a single UPDATE.

        Avoids loading rows into memory, which matters when clearing large
        lists or cascading a parent soft-delete to thousands of children.

        :param db: database session.
        :param conditions: SQLAlchemy / SQLModel ``where`` clauses.
        :returns: number of affected rows (or ``-1`` if the backend cannot
            report rowcount).
        """
        if not hasattr(self.model, "active"):
            raise ValueError(
                f"{self.model.__name__} does not support soft delete"
            )
        statement = (
            update(self.model)
            .where(self.model.active == True, *conditions)
            .values(active=False, deleted_at=datetime.now(UTC))
        )
        result = db.exec(statement)
        db.commit()
        return getattr(result, "rowcount", -1)

    def delete(self, db: Session, id: Any) -> bool:
        """
        Delete an entity by its ID (soft delete if 'active' attribute exists).

        :param db: The database session
        :param id: The ID of the entity to delete
        :return: True if successful, False if the entity was not found
        """
        obj = db.get(self.model, id)
        if obj:
            if hasattr(obj, "active"):
                obj.active = False
                obj.deleted_at = func.now()
                db.add(obj)
            else:
                db.delete(obj)
            db.commit()
            return True
        return False
