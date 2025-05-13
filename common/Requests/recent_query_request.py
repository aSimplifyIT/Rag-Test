from pydantic import BaseModel
from uuid import UUID

class RecentQueryRequest(BaseModel):
    # user_query: str
    assistant_respnose: str
    # conversation_id: UUID = None