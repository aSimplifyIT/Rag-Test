from sqlalchemy import Column, TEXT, func, String, BOOLEAN, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

base_model = declarative_base()

class User(base_model):
    __tablename__ = 'Users'
    Id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    FirstName = Column(String(500), nullable=False)
    LastName = Column(String(500), nullable=False)
    Email = Column(String(250), nullable=False)
    PasswordHash = Column(TEXT)
    CreatedAt = Column(DateTime, nullable=False, default=func.now())
    UpdatedAt = Column(DateTime, nullable=True, onupdate=func.now())
    DeletedAt = Column(DateTime, nullable=True)
    IsDeleted = Column(BOOLEAN, default=False)