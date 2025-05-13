from data.db_connection import DatabaseConnection
from data.models.message import Message
from sqlalchemy import and_
from uuid import UUID
from typing import List

db_connection = DatabaseConnection()

class MessageRepository:
    def __init__(self):
        self.session = db_connection.engine_connection()

    def add_chat_message(self, message_model: Message):
        self.session.add(message_model)
        self.session.commit()

    def get_chat_messages(self, conversation_id: str) -> List[Message]:
        return self.session.query(Message)\
        .filter(and_(Message.ConversationId == UUID(conversation_id), Message.IsDeleted == False))\
        .order_by(Message.CreatedAt)\
        .all()
        
