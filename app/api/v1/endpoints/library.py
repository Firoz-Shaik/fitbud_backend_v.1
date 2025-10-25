# app/api/v1/endpoints/library.py
# API endpoints for managing the exercise and food item libraries.

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.api.deps import CurrentTrainer, DBSession
from app.models.template import ExerciseLibrary, FoodItemLibrary
from app.schemas.library import (
    LibraryExercise, LibraryExerciseCreate, LibraryExerciseUpdate,
    LibraryFoodItem, LibraryFoodItemCreate, LibraryFoodItemUpdate
)
from app.services.library_service import library_service

router = APIRouter()

# --- Exercise Library Endpoints ---

@router.get("/exercises", response_model=List[LibraryExercise])
def get_exercise_library(db: DBSession, current_trainer: CurrentTrainer):
    return library_service.get_exercises(db, trainer_id=current_trainer.id)

@router.post("/exercises", response_model=LibraryExercise, status_code=status.HTTP_201_CREATED)
def create_exercise(exercise_in: LibraryExerciseCreate, db: DBSession, current_trainer: CurrentTrainer):
    return library_service.create_exercise(db, obj_in=exercise_in, trainer_id=current_trainer.id)

@router.put("/exercises/{exercise_id}", response_model=LibraryExercise)
def update_exercise(exercise_id: uuid.UUID, exercise_in: LibraryExerciseUpdate, db: DBSession, current_trainer: CurrentTrainer):
    exercise = db.query(ExerciseLibrary).filter(ExerciseLibrary.id == exercise_id, ExerciseLibrary.deleted_at.is_(None)).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found.")
    if exercise.owner_trainer_id != current_trainer.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this exercise.")
    return library_service.update_exercise(db, exercise=exercise, obj_in=exercise_in)

@router.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: uuid.UUID, db: DBSession, current_trainer: CurrentTrainer):
    exercise = db.query(ExerciseLibrary).filter(ExerciseLibrary.id == exercise_id, ExerciseLibrary.deleted_at.is_(None)).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found.")
    if exercise.owner_trainer_id != current_trainer.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this exercise.")
    library_service.delete_exercise(db, exercise=exercise)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Food Item Library Endpoints ---

@router.get("/food-items", response_model=List[LibraryFoodItem])
def get_food_item_library(db: DBSession, current_trainer: CurrentTrainer):
    return library_service.get_food_items(db, trainer_id=current_trainer.id)

@router.post("/food-items", response_model=LibraryFoodItem, status_code=status.HTTP_201_CREATED)
def create_food_item(food_item_in: LibraryFoodItemCreate, db: DBSession, current_trainer: CurrentTrainer):
    return library_service.create_food_item(db, obj_in=food_item_in, trainer_id=current_trainer.id)

@router.put("/food-items/{food_item_id}", response_model=LibraryFoodItem)
def update_food_item(food_item_id: uuid.UUID, food_item_in: LibraryFoodItemUpdate, db: DBSession, current_trainer: CurrentTrainer):
    food_item = db.query(FoodItemLibrary).filter(FoodItemLibrary.id == food_item_id, FoodItemLibrary.deleted_at.is_(None)).first()
    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found.")
    if food_item.owner_trainer_id != current_trainer.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this food item.")
    return library_service.update_food_item(db, food_item=food_item, obj_in=food_item_in)

@router.delete("/food-items/{food_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_item(food_item_id: uuid.UUID, db: DBSession, current_trainer: CurrentTrainer):
    food_item = db.query(FoodItemLibrary).filter(FoodItemLibrary.id == food_item_id, FoodItemLibrary.deleted_at.is_(None)).first()
    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found.")
    if food_item.owner_trainer_id != current_trainer.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this food item.")
    library_service.delete_food_item(db, food_item=food_item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)