# app/schemas/template.py
# Pydantic models for plan templates.

import uuid
from typing import List, Optional, Any
from pydantic import BaseModel, constr
from datetime import datetime
from .core import CamelCaseModel

# --- Workout Template Schemas ---

class WorkoutSet(CamelCaseModel):
    reps: str  # e.g., "8-12"
    weight: Optional[str] = None # e.g., "50kg" or "Bodyweight"
    rest_seconds: int = 60

class WorkoutItem(CamelCaseModel):
    exercise_name: str # In V2, this could be a UUID from exercise_library
    notes: Optional[str] = None
    sets: List[WorkoutSet]

class WorkoutDay(CamelCaseModel):
    day_name: str # e.g., "Day 1: Upper Body"
    items: List[WorkoutItem]

class WorkoutPlanStructure(CamelCaseModel):
    days: List[WorkoutDay]

class WorkoutPlanTemplateBase(CamelCaseModel):
    name: constr(min_length=1)
    description: Optional[str] = None
    plan_structure: WorkoutPlanStructure

class WorkoutPlanTemplateCreate(WorkoutPlanTemplateBase):
    pass

class WorkoutPlanTemplateUpdate(CamelCaseModel):
    name: Optional[constr(min_length=1)] = None
    description: Optional[str] = None
    plan_structure: Optional[WorkoutPlanStructure] = None

class WorkoutPlanTemplate(WorkoutPlanTemplateBase):
    id: uuid.UUID
    trainer_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

# --- Diet Template Schemas ---

class FoodItem(CamelCaseModel):
    name: str
    quantity: str # e.g., "100g" or "1 cup"
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None

class DietMeal(CamelCaseModel):
    meal_name: str # e.g., "Breakfast"
    items: List[FoodItem]

class DietPlanStructure(CamelCaseModel):
    meals: List[DietMeal]

class DietPlanTemplateBase(CamelCaseModel):
    name: constr(min_length=1)
    description: Optional[str] = None
    plan_structure: DietPlanStructure

class DietPlanTemplateCreate(DietPlanTemplateBase):
    pass

class DietPlanTemplateUpdate(CamelCaseModel):
    name: Optional[constr(min_length=1)] = None
    description: Optional[str] = None
    plan_structure: Optional[DietPlanStructure] = None

class DietPlanTemplate(DietPlanTemplateBase):
    id: uuid.UUID
    trainer_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

