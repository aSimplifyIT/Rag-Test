from pydantic import BaseModel
from uuid import UUID

class ConversationRead(BaseModel):
    id: UUID
    name: str