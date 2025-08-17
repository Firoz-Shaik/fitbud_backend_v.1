# app/models/log.py
# SQLAlchemy ORM models for logging tables.

from sqlalchemy import Column, DateTime, func, ForeignKey, String, BigInteger, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class WorkoutLog(Base):
    __tablename__ = "workout_logs"
    id = Column(BigInteger, primary_key=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    assigned_plan_id = Column(UUID(as_uuid=True), ForeignKey("assigned_workout_plans.id", ondelete="CASCADE"), nullable=False)
    performance_data = Column(JSONB, nullable=True)
    logged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    client = relationship("Client", back_populates="workout_logs")

class DietLog(Base):
    __tablename__ = "diet_logs"
    id = Column(BigInteger, primary_key=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    assigned_plan_id = Column(UUID(as_uuid=True), ForeignKey("assigned_diet_plans.id", ondelete="CASCADE"), nullable=False)
    meal_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    logged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    client = relationship("Client", back_populates="diet_logs")

class Checkin(Base):
    __tablename__ = "checkins"
    id = Column(BigInteger, primary_key=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    weight_kg = Column(Numeric(6, 2), nullable=True)
    measurements = Column(JSONB, nullable=True)
    progress_photo_url = Column(String, nullable=True)
    subjective_scores = Column(JSONB, nullable=True)
    notes = Column(String, nullable=True)
    checked_in_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    client = relationship("Client", back_populates="checkins")