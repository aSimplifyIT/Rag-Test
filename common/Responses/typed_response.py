from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar("T")

class TypedResponse(BaseModel, Generic[T]):
    has_error: bool
    status_code: int
    errors: List[str] = []
    result: Optional[T] = None