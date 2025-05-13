from typing import TypeVar, Generic, Optional
from pydantic import BaseModel
from uuid import UUID

T = TypeVar("T")

class MessageRead(BaseModel, Generic[T]):
    id: UUID
    message: Optional[T]
    role: str

