from sqlmodel import Session, select, func, SQLModel
from typing import Generic, TypeVar, Type, Optional, Sequence, Any, Dict, Tuple
from utils.pagination import PaginationParams

T = TypeVar("T", bound=SQLModel)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, db: Session, id: Any) -> Optional[T]:
        return db.get(self.model, id)

    def get_all(self, db: Session, params: PaginationParams, filters: Dict[str, Any] = None) -> Tuple[Sequence[T], int]:
        statement = select(self.model)
        
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
        db.add(obj_in)
        db.commit()
        db.refresh(obj_in)
        return obj_in

    def update(self, db: Session, db_obj: T, obj_in: Dict[str, Any]) -> T:
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: Any) -> bool:
        obj = db.get(self.model, id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
