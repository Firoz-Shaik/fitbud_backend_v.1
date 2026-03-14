# app/schemas/library.py
# Pydantic models for the exercise and food item libraries.

import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, constr
from .core import CamelCaseModel

# --- Exercise Library Schemas ---

class LibraryExerciseBase(CamelCaseModel):
    name: constr(min_length=1)
    description: Optional[str] = None

class LibraryExerciseCreate(LibraryExerciseBase):
    pass

class LibraryExerciseUpdate(LibraryExerciseBase):
    pass

class LibraryExercise(LibraryExerciseBase):
    id: uuid.UUID
    is_verified: bool
    owner_trainer_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)

# --- Food Item Library Schemas ---

class LibraryFoodItemBase(CamelCaseModel):
    name: constr(min_length=1)
    base_unit_type: Optional[str] = None  # MASS or VOLUME
    grams_per_ml: Optional[float] = None
    calories_per_100g: Optional[int] = None
    protein_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None

class LibraryFoodItemCreate(LibraryFoodItemBase):
    pass

class LibraryFoodItemUpdate(LibraryFoodItemBase):
    pass

class LibraryFoodItem(LibraryFoodItemBase):
    id: uuid.UUID
    is_verified: bool
    owner_trainer_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)