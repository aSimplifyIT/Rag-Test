from data.models.base import Base
from data.models.user import User
from sqlalchemy import Column, ForeignKey, TEXT
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

base_model = declarative_base()

class Conversation(Base, base_model):
    __tablename__ = 'Conversations'
    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    Name=Column(TEXT, nullable=False)
    UserId = Column(UUID(as_uuid=True), ForeignKey(User.Id), nullable=False)