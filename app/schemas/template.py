# app/schemas/template.py
# Pydantic models for plan templates, updated for the new V2 normalized structure.

import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, computed_field, constr
from datetime import datetime
from app.core.units import calculate_nutrition
from .core import CamelCaseModel
from .library import LibraryExercise, LibraryFoodItem

# --- Refined objects for the new WORKOUT API structure ---

class WorkoutTarget(CamelCaseModel):
    sets: str
    reps: str
    rest_period_seconds: Optional[int] = None
    notes: Optional[str] = None

class WorkoutTemplateItemGet(CamelCaseModel):
    item_id: int = Field(validation_alias="id")
    day_name: str
    display_order: Optional[int] = None
    exercise: LibraryExercise
    target_sets: Optional[str] = Field(default=None, exclude=True)
    target_reps: Optional[str] = Field(default=None, exclude=True)
    rest_period_seconds: Optional[int] = Field(default=None, exclude=True)
    notes: Optional[str] = Field(default=None, exclude=True)

    @computed_field
    @property
    def targets(self) -> WorkoutTarget:
        return WorkoutTarget(
            sets=self.target_sets or "",
            reps=self.target_reps or "",
            rest_period_seconds=self.rest_period_seconds,
            notes=self.notes,
        )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class WorkoutTemplateItemCreate(CamelCaseModel):
    exercise_id: uuid.UUID
    day_name: str
    display_order: Optional[int] = None
    targets: Optional[WorkoutTarget] = None
    target_sets: Optional[str] = None  # Accept flat format from API
    target_reps: Optional[str] = None
    rest_period_seconds: Optional[int] = None  # Accept flat format from API
    notes: Optional[str] = None

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
    item_id: int = Field(validation_alias="id")
    meal_name: str
    display_order: Optional[int] = None
    food_item: LibraryFoodItem
    serving_size: Optional[float] = Field(default=None, exclude=True)
    serving_unit: Optional[str] = Field(default=None, exclude=True)

    @computed_field
    @property
    def serving(self) -> Serving:
        return Serving(size=float(self.serving_size or 0), unit=self.serving_unit or "g")

    @computed_field
    @property
    def calculated_nutrition(self) -> CalculatedNutrition:
        nut = calculate_nutrition(self.food_item, float(self.serving_size or 0), self.serving_unit or "g")
        return CalculatedNutrition(
            calories=nut["calories"],
            protein_g=nut["protein_g"],
            carbs_g=nut["carbs_g"],
            fat_g=nut["fat_g"],
        )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

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

    model_config = ConfigDict(from_attributes=True)

class DietPlanTemplateCreate(PlanTemplateBase):
    items: List[DietTemplateItemCreate]

class DietPlanTemplateUpdate(PlanTemplateBase):
    items: List[DietTemplateItemCreate]

class DietPlanTemplate(PlanTemplateBase):
    id: uuid.UUID
    trainer_id: uuid.UUID
    created_at: datetime
    items: List[DietTemplateItemGet]

    model_config = ConfigDict(from_attributes=True)