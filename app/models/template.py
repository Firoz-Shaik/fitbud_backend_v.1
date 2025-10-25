# app/models/template.py
# SQLAlchemy ORM models for plan templates, updated for V2 structure.

import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Integer, BigInteger, Text, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

# --- NEW V2 LIBRARY MODELS ---

class ExerciseLibrary(Base):
    __tablename__ = "exercise_library"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    owner_trainer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

class FoodItemLibrary(Base):
    __tablename__ = "food_item_library"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    owner_trainer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    base_unit_type = Column(String, nullable=True) # MASS or VOLUME
    grams_per_ml = Column(Numeric, nullable=True)
    calories_per_100g = Column(Integer, nullable=True)
    protein_per_100g = Column(Numeric, nullable=True)
    carbs_per_100g = Column(Numeric, nullable=True)
    fat_per_100g = Column(Numeric, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

# --- NEW V2 LINKING MODELS ---

class WorkoutTemplateItem(Base):
    __tablename__ = "workout_template_items"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("workout_plan_templates.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercise_library.id", ondelete="RESTRICT"), nullable=False)
    day_name = Column(String, nullable=False)
    target_sets = Column(String, nullable=True)
    target_reps = Column(String, nullable=True)
    rest_period_seconds = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    display_order = Column(Integer)
    
    exercise = relationship("ExerciseLibrary")

class DietTemplateItem(Base):
    __tablename__ = "diet_template_items"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("diet_plan_templates.id", ondelete="CASCADE"), nullable=False)
    food_item_id = Column(UUID(as_uuid=True), ForeignKey("food_item_library.id", ondelete="RESTRICT"), nullable=False)
    meal_name = Column(String, nullable=False)
    serving_size = Column(Numeric, nullable=True)
    serving_unit = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    display_order = Column(Integer)

    food_item = relationship("FoodItemLibrary")

# --- UPDATED TEMPLATE MODELS (Parent Tables) ---

class WorkoutPlanTemplate(Base):
    __tablename__ = "workout_plan_templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    parent_template_id = Column(UUID(as_uuid=True), ForeignKey("workout_plan_templates.id", ondelete="SET NULL"), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    items = relationship("WorkoutTemplateItem", cascade="all, delete-orphan")

class DietPlanTemplate(Base):
    __tablename__ = "diet_plan_templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    parent_template_id = Column(UUID(as_uuid=True), ForeignKey("diet_plan_templates.id", ondelete="SET NULL"), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    items = relationship("DietTemplateItem", cascade="all, delete-orphan")