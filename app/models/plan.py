# app/models/plan.py
# SQLAlchemy ORM models for assigned plans.

import uuid
from sqlalchemy import Column, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class AssignedWorkoutPlan(Base):
    __tablename__ = "assigned_workout_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    source_template_id = Column(UUID(as_uuid=True), ForeignKey("workout_plan_templates.id", ondelete="SET NULL"), nullable=True)
    plan_details = Column(JSONB, nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    client = relationship("Client", back_populates="assigned_workout_plans")
    source_template = relationship("WorkoutPlanTemplate")

class AssignedDietPlan(Base):
    __tablename__ = "assigned_diet_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    source_template_id = Column(UUID(as_uuid=True), ForeignKey("diet_plan_templates.id", ondelete="SET NULL"), nullable=True)
    plan_details = Column(JSONB, nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    client = relationship("Client", back_populates="assigned_diet_plans")
    source_template = relationship("DietPlanTemplate")
