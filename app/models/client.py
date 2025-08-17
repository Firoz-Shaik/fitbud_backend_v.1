# app/models/client.py
# SQLAlchemy ORM model for the 'clients' table.

import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainer_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    client_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=True, unique=True)
    status = Column(String, nullable=False) # 'invited', 'active', 'inactive'
    goal = Column(String, nullable=True)
    goal_description = Column(Text, nullable=True)
    invited_full_name = Column(String, nullable=True)
    invited_email = Column(String, nullable=True)
    private_notes = Column(Text, nullable=True)
    invite_code = Column(String, unique=True, nullable=True)
    
    # --- NEW V1.1 COLUMNS ---
    subscription_due_date = Column(DateTime(timezone=True), nullable=True)
    subscription_paid_status = Column(Boolean, nullable=True, default=False)
    initial_weight_kg = Column(Numeric(6, 2), nullable=True)
    height_cm = Column(Numeric(5, 1), nullable=True)
    health_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    trainer_user = relationship("User", foreign_keys=[trainer_user_id], back_populates="trainer_clients")
    client_user = relationship("User", foreign_keys=[client_user_id], back_populates="client_profile")
    
    assigned_workout_plans = relationship("AssignedWorkoutPlan", back_populates="client", cascade="all, delete-orphan")
    assigned_diet_plans = relationship("AssignedDietPlan", back_populates="client", cascade="all, delete-orphan")
    workout_logs = relationship("WorkoutLog", back_populates="client", cascade="all, delete-orphan")
    diet_logs = relationship("DietLog", back_populates="client", cascade="all, delete-orphan")
    checkins = relationship("Checkin", back_populates="client", cascade="all, delete-orphan")
    activity_feed = relationship("ActivityFeed", back_populates="client", cascade="all, delete-orphan")
