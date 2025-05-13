from data.models.base import Base
from data.models.conversation import Conversation
from sqlalchemy import Column, ForeignKey, TEXT, INT
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid


base_model = declarative_base()

class Message(Base, base_model):
    __tablename__ = 'Files'
    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    Name=Column(TEXT, nullable=False)