from pydantic import BaseModel
from uuid import UUID
from typing import Literal, List, Union, Optional

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ConversationRequest(BaseModel):
    user_query: str
    chat_history: Optional[List[ChatMessage]] = None