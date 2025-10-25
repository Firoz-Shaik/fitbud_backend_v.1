# app/schemas/template.py
# Pydantic models for plan templates, updated for the new V2 normalized structure.

import uuid
from typing import List, Optional
from pydantic import BaseModel, constr
from datetime import datetime
from .core import CamelCaseModel
from .library import LibraryExercise, LibraryFoodItem

# --- Refined objects for the new WORKOUT API structure ---

class WorkoutTarget(CamelCaseModel):
    sets: str
    reps: str
    rest_period_seconds: Optional[int] = None
    notes: Optional[str] = None

class WorkoutTemplateItemGet(CamelCaseModel):
    item_id: int
    day_name: str
    display_order: Optional[int] = None
    exercise: LibraryExercise
    targets: WorkoutTarget

    class Config:
        from_attributes = True

class WorkoutTemplateItemCreate(CamelCaseModel):
    exercise_id: uuid.UUID
    day_name: str
    display_order: Optional[int] = None
    targets: WorkoutTarget

# --- Refined objects for the new DIET API structure ---

class Serving(CamelCaseModel):
    size: float
    unit: str

class CalculatedNutrition(CamelCaseModel):
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float

class DietTemplateItemGet(CamelCaseModel):
    item_id: int
    meal_name: str
    display_order: Optional[int] = None
    food_item: LibraryFoodItem
    serving: Serving
    calculated_nutrition: CalculatedNutrition

    class Config:
        from_attributes = True

class DietTemplateItemCreate(CamelCaseModel):
    food_item_id: uuid.UUID
    meal_name: str
    display_order: Optional[int] = None
    serving: Serving

# --- Main Template Schemas ---

class PlanTemplateBase(CamelCaseModel):
    name: constr(min_length=1)
    description: Optional[str] = None

class WorkoutPlanTemplateCreate(PlanTemplateBase):
    items: List[WorkoutTemplateItemCreate]

class WorkoutPlanTemplateUpdate(PlanTemplateBase):
    items: List[WorkoutTemplateItemCreate]

class WorkoutPlanTemplate(PlanTemplateBase):
    id: uuid.UUID
    trainer_id: uuid.UUID
    created_at: datetime
    items: List[WorkoutTemplateItemGet]

    class Config:
        from_attributes = True

class DietPlanTemplateCreate(PlanTemplateBase):
    items: List[DietTemplateItemCreate]

class DietPlanTemplateUpdate(PlanTemplateBase):
    items: List[DietTemplateItemCreate]

class DietPlanTemplate(PlanTemplateBase):
    id: uuid.UUID
    trainer_id: uuid.UUID
    created_at: datetime
    items: List[DietTemplateItemGet]

    class Config:
        from_attributes = True