from data.repository.message_repository import MessageRepository
from data.models.message import Message
from common.enums import MessageRole
from common.Responses.message_read import MessageRead
from uuid import UUID
from typing import List
import json

message_repository = MessageRepository()

class MessageService:
    def add_chat_message(self, message: str, conversation_id: UUID, user_id: str, role: MessageRole):
        message_model = Message(
            Message = message,
            Role = role.value,
            ConversationId = conversation_id,
            CreatedBy = UUID(user_id),
            UpdatedBy = UUID(user_id)
        )
        message_repository.add_chat_message(message_model)

    def get_chat_messages(self, conversation_id: str) -> List[MessageRead]:
        try:
            messages = message_repository.get_chat_messages(conversation_id)
            messages_read = [
                MessageRead(
                    id=message.Id,
                    message=json.loads(message.Message) if message.Role == MessageRole.ASSISTANT.value else message.Message,
                    role=MessageRole(message.Role).name
                )
                for message in messages
            ]

            return messages_read
        
        except json.JSONDecodeError as e:
            print("JSON Decode Exception:", e)

        except Exception as e:
            print("Exception: ", e)