# app/models/activity.py
# SQLAlchemy ORM model for the 'activity_feed' table.

from sqlalchemy import Column, DateTime, func, ForeignKey, String, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class ActivityFeed(Base):
    __tablename__ = "activity_feed"
    id = Column(BigInteger, primary_key=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String, nullable=False)
    event_timestamp = Column(DateTime(timezone=True), nullable=False)
    event_metadata = Column(JSONB, nullable=True)

    client = relationship("Client", back_populates="activity_feed")
