# app/services/library_service.py
# Business logic for managing the exercise and food item libraries.

import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from app.models.template import ExerciseLibrary, FoodItemLibrary
from app.schemas.library import LibraryExerciseCreate, LibraryExerciseUpdate, LibraryFoodItemCreate, LibraryFoodItemUpdate

class LibraryService:
    # --- Exercise Library Methods ---

    def get_exercises(self, db: Session, *, trainer_id: uuid.UUID) -> List[ExerciseLibrary]:
        """
        Retrieves all exercises that are either global (is_verified=true) or owned by the trainer.
        """
        return db.query(ExerciseLibrary).filter(
            or_(ExerciseLibrary.is_verified == True, ExerciseLibrary.owner_trainer_id == trainer_id),
            ExerciseLibrary.deleted_at.is_(None)
        ).all()

    def create_exercise(self, db: Session, *, obj_in: LibraryExerciseCreate, trainer_id: uuid.UUID) -> ExerciseLibrary:
        """
        Creates a new, private exercise for a trainer.
        """
        db_obj = ExerciseLibrary(
            **obj_in.model_dump(),
            owner_trainer_id=trainer_id,
            is_verified=False
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_exercise(self, db: Session, *, exercise: ExerciseLibrary, obj_in: LibraryExerciseUpdate) -> ExerciseLibrary:
        """
        Updates an exercise.
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(exercise, field, value)
        db.add(exercise)
        db.commit()
        db.refresh(exercise)
        return exercise

    def delete_exercise(self, db: Session, *, exercise: ExerciseLibrary) -> None:
        """
        Soft deletes an exercise.
        """
        exercise.deleted_at = datetime.utcnow()
        db.add(exercise)
        db.commit()
        return

    # --- Food Item Library Methods ---

    def get_food_items(self, db: Session, *, trainer_id: uuid.UUID) -> List[FoodItemLibrary]:
        """
        Retrieves all food items that are either global or owned by the trainer.
        """
        return db.query(FoodItemLibrary).filter(
            or_(FoodItemLibrary.is_verified == True, FoodItemLibrary.owner_trainer_id == trainer_id),
            FoodItemLibrary.deleted_at.is_(None)
        ).all()

    def create_food_item(self, db: Session, *, obj_in: LibraryFoodItemCreate, trainer_id: uuid.UUID) -> FoodItemLibrary:
        """
        Creates a new, private food item for a trainer.
        """
        db_obj = FoodItemLibrary(
            **obj_in.model_dump(),
            owner_trainer_id=trainer_id,
            is_verified=False
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_food_item(self, db: Session, *, food_item: FoodItemLibrary, obj_in: LibraryFoodItemUpdate) -> FoodItemLibrary:
        """
        Updates a food item.
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(food_item, field, value)
        db.add(food_item)
        db.commit()
        db.refresh(food_item)
        return food_item

    def delete_food_item(self, db: Session, *, food_item: FoodItemLibrary) -> None:
        """
        Soft deletes a food item.
        """
        food_item.deleted_at = datetime.utcnow()
        db.add(food_item)
        db.commit()
        return

library_service = LibraryService()