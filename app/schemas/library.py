# app/schemas/library.py (NEW FILE)
# Pydantic models for the static exercise and meal libraries.

from typing import List, Optional
from pydantic import BaseModel
from .core import CamelCaseModel
class LibraryExercise(CamelCaseModel):
    id: str
    name: str
    description: Optional[str] = None

class LibraryMealItem(CamelCaseModel):
    id: str
    name: str
    # Simplified nutritional info for V1
    category: str # e.g., "Protein", "Carbohydrate", "Fat", "Vegetable"