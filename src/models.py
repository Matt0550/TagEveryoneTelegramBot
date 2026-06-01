from pydantic import BaseModel
from typing import Any, TypeVar, Generic
from fastapi.responses import JSONResponse

# * FASTAPI MODELS

from sqlmodel import SQLModel

class ModelBase(SQLModel):
    pass

T = TypeVar("T")


class GenericResponse(BaseModel, Generic[T]):
    message: T
    success: bool = True
    status_code: int


class CustomResponse(JSONResponse):
    def __init__(self, content: Any, status_code: Any = 200, *args, **kwargs):
        # Support either int or enum/class with a .value attribute
        status_code_int = int(getattr(status_code, "value", status_code))

        # Customize content and pass my new content...
        from pydantic import BaseModel

        if isinstance(content, GenericResponse):
            payload = content.model_dump()
        elif isinstance(content, BaseModel):
            payload = {
                "message": content.model_dump(),
                "success": False if status_code_int != 200 else True,
                "status_code": status_code_int,
            }
        elif (
            isinstance(content, dict)
            and "message" in content
            and "success" in content
            and "status_code" in content
        ):
            payload = content
        else:
            payload = {
                "message": content,
                "success": False if status_code_int != 200 else True,
                "status_code": status_code_int,
            }
        super().__init__(*args, content=payload, status_code=status_code_int, **kwargs)
