# app/api/v1/endpoints/library.py (NEW FILE)
# API endpoints for accessing static library content.

from typing import List
from fastapi import APIRouter, Depends

from app.api.deps import CurrentTrainer
from app.schemas.library import LibraryExercise, LibraryMealItem
from app.services.library_service import library_service

router = APIRouter()

@router.get("/exercises", response_model=List[LibraryExercise])
def get_exercise_library(current_trainer: CurrentTrainer):
    """
    Get the static list of exercises for the plan builder.
    (Trainer only)
    """
    return library_service.get_exercises()

@router.get("/meals", response_model=List[LibraryMealItem])
def get_meal_library(current_trainer: CurrentTrainer):
    """
    Get the static list of meal items for the plan builder.
    (Trainer only)
    """
    return library_service.get_meal_items()