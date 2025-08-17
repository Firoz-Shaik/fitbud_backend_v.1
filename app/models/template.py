# app/models/template.py
# SQLAlchemy ORM models for plan templates. (UPDATED)

import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB # Added JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class WorkoutPlanTemplate(Base):
    __tablename__ = "workout_plan_templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    plan_structure = Column(JSONB, nullable=False) # NEW COLUMN
    # V2 fields
    parent_template_id = Column(UUID(as_uuid=True), ForeignKey("workout_plan_templates.id", ondelete="SET NULL"), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

class DietPlanTemplate(Base):
    __tablename__ = "diet_plan_templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    plan_structure = Column(JSONB, nullable=False) # NEW COLUMN
    # V2 fields
    parent_template_id = Column(UUID(as_uuid=True), ForeignKey("diet_plan_templates.id", ondelete="SET NULL"), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
