# app/models/user.py
# SQLAlchemy ORM model for the 'users' table.

import uuid
from sqlalchemy import Column, String, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    user_role = Column(String, nullable=False) # 'trainer' or 'client'
    profile_photo_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    trainer_clients = relationship("Client", foreign_keys="Client.trainer_user_id", back_populates="trainer_user")
    client_profile = relationship(
        "Client", 
        foreign_keys="Client.client_user_id", # <-- 2. SPECIFY THE EXACT FOREIGN KEY
        back_populates="client_user", 
        uselist=False
    )
    __table_args__ = (
        # This corresponds to the partial unique index in the SQL file.
        Index("users_email_unique_when_active_idx", "email", unique=True, postgresql_where=(deleted_at.is_(None))),
        {"schema": None},
    )
