# app/services/template_service.py
# Business logic updated for V2 with nutrition calculation.

from typing import List, Optional
import uuid
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from fastapi import HTTPException, status
from app.models.template import (
    WorkoutPlanTemplate, 
    DietPlanTemplate, 
    WorkoutTemplateItem, 
    DietTemplateItem,
    FoodItemLibrary
)
from app.schemas.template import (
    WorkoutPlanTemplateCreate, 
    WorkoutPlanTemplateUpdate,
    DietPlanTemplateCreate,
    DietPlanTemplateUpdate
)
from app.core.units import UNIT_DICTIONARY, calculate_nutrition

class TemplateService:
    
    def _calculate_nutrition(self, food_item: FoodItemLibrary, serving_size: float, serving_unit: str) -> dict:
        """Calculates nutrition for a given food item and serving size. Raises HTTPException for invalid units."""
        unit_info = UNIT_DICTIONARY.get((serving_unit or "").lower())
        if not unit_info:
            raise HTTPException(status_code=400, detail=f"Unit '{serving_unit}' is not a valid unit.")
        if unit_info["type"] == "VOLUME" and (food_item.base_unit_type != "VOLUME" or not food_item.grams_per_ml):
            raise HTTPException(status_code=400, detail=f"Cannot perform volume to mass conversion for '{food_item.name}'.")
        return calculate_nutrition(food_item, serving_size, serving_unit)

    # --- Workout Plan Template Methods ---
    def create_workout_template(self, db: Session, *, obj_in: WorkoutPlanTemplateCreate, trainer_id: uuid.UUID) -> WorkoutPlanTemplate:
        db_template = WorkoutPlanTemplate(name=obj_in.name, description=obj_in.description, trainer_id=trainer_id)
        db.add(db_template)
        db.flush()
        for item_in in obj_in.items:
            dump = item_in.model_dump(exclude={"targets", "target_sets", "target_reps", "rest_period_seconds", "notes"})
            sets_val = (item_in.targets.sets if item_in.targets else item_in.target_sets) or ""
            reps_val = (item_in.targets.reps if item_in.targets else item_in.target_reps) or ""
            dump["target_sets"] = sets_val
            dump["target_reps"] = reps_val
            dump["rest_period_seconds"] = (
                item_in.targets.rest_period_seconds if item_in.targets else item_in.rest_period_seconds
            )
            dump["notes"] = item_in.targets.notes if item_in.targets else item_in.notes
            db.add(WorkoutTemplateItem(template_id=db_template.id, **dump))
        db.commit()
        db.refresh(db_template)
        return db_template

    def get_workout_template(self, db: Session, *, template_id: uuid.UUID, trainer_id: uuid.UUID) -> Optional[WorkoutPlanTemplate]:
        return db.query(WorkoutPlanTemplate).options(joinedload(WorkoutPlanTemplate.items).joinedload(WorkoutTemplateItem.exercise)).filter(WorkoutPlanTemplate.id == template_id, WorkoutPlanTemplate.trainer_id == trainer_id, WorkoutPlanTemplate.deleted_at.is_(None)).first()
    
    def get_workout_templates(self, db: Session, *, trainer_id: uuid.UUID, skip: int, limit: int) -> List[WorkoutPlanTemplate]:
        """Retrieves a paginated list of workout templates for a specific trainer."""
        return db.query(WorkoutPlanTemplate).filter(
            WorkoutPlanTemplate.trainer_id == trainer_id,
            WorkoutPlanTemplate.deleted_at.is_(None)
        ).order_by(WorkoutPlanTemplate.updated_at.desc()).offset(skip).limit(limit).all()
    
    def update_workout_template(self, db: Session, *, template: WorkoutPlanTemplate, obj_in: WorkoutPlanTemplateUpdate) -> WorkoutPlanTemplate:
        template.name = obj_in.name
        template.description = obj_in.description
        db.query(WorkoutTemplateItem).filter(WorkoutTemplateItem.template_id == template.id).delete()
        for item_in in obj_in.items:
            dump = item_in.model_dump(exclude={"targets", "target_sets", "target_reps", "rest_period_seconds", "notes"})
            sets_val = (item_in.targets.sets if item_in.targets else item_in.target_sets) or ""
            reps_val = (item_in.targets.reps if item_in.targets else item_in.target_reps) or ""
            dump["target_sets"] = sets_val
            dump["target_reps"] = reps_val
            dump["rest_period_seconds"] = (
                item_in.targets.rest_period_seconds if item_in.targets else item_in.rest_period_seconds
            )
            dump["notes"] = item_in.targets.notes if item_in.targets else item_in.notes
            db.add(WorkoutTemplateItem(template_id=template.id, **dump))
        db.commit()
        db.refresh(template)
        return template

    def delete_workout_template(self, db: Session, *, template: WorkoutPlanTemplate) -> None:
        template.deleted_at = datetime.utcnow()
        db.add(template)
        db.commit()

    # --- Diet Plan Template Methods ---
    def create_diet_template(self, db: Session, *, obj_in: DietPlanTemplateCreate, trainer_id: uuid.UUID) -> DietPlanTemplate:
        db_template = DietPlanTemplate(name=obj_in.name, description=obj_in.description, trainer_id=trainer_id)
        db.add(db_template)
        db.flush()
        for item_in in obj_in.items:
            food_item = db.query(FoodItemLibrary).filter(FoodItemLibrary.id == item_in.food_item_id).first()
            if not food_item:
                raise HTTPException(status_code=404, detail=f"Food item with id {item_in.food_item_id} not found.")
            
            db.add(DietTemplateItem(
                template_id=db_template.id,
                food_item_id=item_in.food_item_id,
                meal_name=item_in.meal_name,
                display_order=item_in.display_order,
                serving_size=item_in.serving.size,
                serving_unit=item_in.serving.unit,
            ))
        
        db.commit()
        db.refresh(db_template)
        return db_template

    def get_diet_template(self, db: Session, *, template_id: uuid.UUID, trainer_id: uuid.UUID) -> Optional[DietPlanTemplate]:
        return db.query(DietPlanTemplate).options(joinedload(DietPlanTemplate.items).joinedload(DietTemplateItem.food_item)).filter(DietPlanTemplate.id == template_id, DietPlanTemplate.trainer_id == trainer_id, DietPlanTemplate.deleted_at.is_(None)).first()
    
    def get_diet_templates(self, db: Session, *, trainer_id: uuid.UUID, skip: int, limit: int) -> List[DietPlanTemplate]:
        """Retrieves a paginated list of diet templates for a specific trainer."""
        return db.query(DietPlanTemplate).filter(
            DietPlanTemplate.trainer_id == trainer_id,
            DietPlanTemplate.deleted_at.is_(None)
        ).order_by(DietPlanTemplate.updated_at.desc()).offset(skip).limit(limit).all()
    
    def update_diet_template(self, db: Session, *, template: DietPlanTemplate, obj_in: DietPlanTemplateUpdate) -> DietPlanTemplate:
        template.name = obj_in.name
        template.description = obj_in.description
        db.query(DietTemplateItem).filter(DietTemplateItem.template_id == template.id).delete()
        for item_in in obj_in.items:
            food_item = db.query(FoodItemLibrary).filter(FoodItemLibrary.id == item_in.food_item_id).first()
            if not food_item:
                raise HTTPException(status_code=404, detail=f"Food item with id {item_in.food_item_id} not found.")
            
            db.add(DietTemplateItem(
                template_id=template.id,
                food_item_id=item_in.food_item_id,
                meal_name=item_in.meal_name,
                display_order=item_in.display_order,
                serving_size=item_in.serving.size,
                serving_unit=item_in.serving.unit,
            ))
            
        db.commit()
        db.refresh(template)
        return template

    def delete_diet_template(self, db: Session, *, template: DietPlanTemplate) -> None:
        template.deleted_at = datetime.utcnow()
        db.add(template)
        db.commit()
    
    def create_workout_plan_snapshot(self, *, template: WorkoutPlanTemplate) -> dict:
        """Builds a rich JSON snapshot from a workout template's relational items."""
        return {
            "name": template.name,
            "description": template.description,
            "items": [
                {
                    "itemId": item.id,
                    "dayName": item.day_name,
                    "displayOrder": item.display_order,
                    "exercise": {
                        # JSONB must not contain UUID objects (psycopg2 can't serialize them)
                        "id": str(item.exercise.id),
                        "name": item.exercise.name,
                        "description": item.exercise.description
                    },
                    "targets": {
                        "sets": item.target_sets,
                        "reps": item.target_reps,
                        "rest_period_seconds": item.rest_period_seconds,
                        "notes": item.notes
                    }
                } for item in template.items
            ]
        }

    def create_diet_plan_snapshot(self, *, template: DietPlanTemplate) -> dict:
        """Builds a rich JSON snapshot from a diet template's relational items."""
        return {
            "name": template.name,
            "description": template.description,
            "items": [
                {
                    "itemId": item.id,
                    "mealName": item.meal_name,
                    "displayOrder": item.display_order,
                    "foodItem": {
                        # JSONB must not contain UUID objects (psycopg2 can't serialize them)
                        "id": str(item.food_item.id),
                        "name": item.food_item.name
                    },
                    "serving": {
                        "size": float(item.serving_size or 0),
                        "unit": item.serving_unit or "g"
                    },
                    "notes": item.notes,
                    "calculatedNutrition": self._calculate_nutrition(
                        food_item=item.food_item,
                        serving_size=float(item.serving_size or 0),
                        serving_unit=item.serving_unit or "g"
                    )
                } for item in template.items
            ]
        }

template_service = TemplateService()