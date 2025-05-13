from data.db_connection import DatabaseConnection
from data.models.conversation import Conversation
from sqlalchemy import and_, desc
from typing import List
from uuid import UUID

db_connection = DatabaseConnection()

class ConversationRepository:
    def __init__(self):
        self.session = db_connection.engine_connection()

    def create_conversation(self, conversation_model: Conversation):
        self.session.add(conversation_model)
        self.session.commit()

    def update_conversation(self, conversation: Conversation):
        self.session.merge(conversation)
        self.session.commit()

    def get_conversations_by_user_id(self, user_id: str) -> List[Conversation]:
        return self.session.query(Conversation)\
        .filter(and_(Conversation.UserId == UUID(user_id), Conversation.IsDeleted == False))\
        .order_by(desc(Conversation.CreatedAt))\
        .all()
    
    def get_conversation_by_id(self, conversation_id: str) -> Conversation:
        return self.session.query(Conversation)\
        .filter(and_(Conversation.Id == UUID(conversation_id), Conversation.IsDeleted == False))\
        .first()