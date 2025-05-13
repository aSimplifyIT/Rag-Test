from pydantic import BaseModel
from uuid import UUID

class UserRead(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str