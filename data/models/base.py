from sqlalchemy import Column, BOOLEAN, func, DateTime
from sqlalchemy.dialects.postgresql import UUID

class Base():
    __abstract__ = True

    CreatedAt = Column(DateTime, nullable=False, default=func.now())
    CreatedBy = Column(UUID(as_uuid=True), nullable=False)
    UpdatedAt = Column(DateTime, nullable=False, default=func.now())
    UpdatedBy = Column(UUID(as_uuid=True), nullable=False)
    DeletedAt = Column(DateTime, nullable=True)
    DeletedBy = Column(UUID(as_uuid=True), nullable=True)
    IsDeleted = Column(BOOLEAN, default=False)
