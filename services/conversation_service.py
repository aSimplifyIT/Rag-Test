from data.repository.conversation_repository import ConversationRepository
from data.models.conversation import Conversation
from common.Responses.conversation_read import ConversationRead
from typing import List
from uuid import UUID
from sqlalchemy import func

conversation_repository = ConversationRepository()

class ConversationService:
    def create_conversation(self, user_query: str, user_id: str) -> UUID:
        conversation_model = Conversation(
            Name = user_query,
            UserId = UUID(user_id),
            CreatedBy = UUID(user_id),
            UpdatedBy = UUID(user_id)
        )

        conversation_repository.create_conversation(conversation_model)
        return conversation_model.Id

    def get_conversations_by_user_id(self, user_id: str) -> List[ConversationRead]:
        conversations = conversation_repository.get_conversations_by_user_id(user_id)
        conversations_read = [
            ConversationRead(
                id=conversation.Id,
                name=conversation.Name,
            )
            for conversation in conversations
        ]

        return conversations_read

    def update_conversation(self):
        pass

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        conversation = conversation_repository.get_conversation_by_id(conversation_id)
        if conversation:
            conversation.IsDeleted = True
            conversation.DeletedBy = user_id
            conversation.DeletedAt = func.now()
            conversation_repository.update_conversation(conversation)
            return True
        else:
            return False