# app/services/template_service.py
# Business logic for managing workout and diet plan templates.

from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from datetime import datetime # IMPORT ADDED
from app.models.template import WorkoutPlanTemplate, DietPlanTemplate
from app.schemas.template import WorkoutPlanTemplateCreate, WorkoutPlanTemplateUpdate, DietPlanTemplateCreate, DietPlanTemplateUpdate

class TemplateService:
    # --- Workout Plan Template Methods ---

    def create_workout_template(self, db: Session, *, obj_in: WorkoutPlanTemplateCreate, trainer_id: uuid.UUID) -> WorkoutPlanTemplate:
        db_obj = WorkoutPlanTemplate(
            **obj_in.model_dump(),
            trainer_id=trainer_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_workout_template(self, db: Session, *, template_id: uuid.UUID, trainer_id: uuid.UUID) -> Optional[WorkoutPlanTemplate]:
        """
        Retrieves a single workout template by its ID, ensuring it belongs to the specified trainer.
        """
        return db.query(WorkoutPlanTemplate).filter(
            WorkoutPlanTemplate.id == template_id,
            WorkoutPlanTemplate.trainer_id == trainer_id,
            WorkoutPlanTemplate.deleted_at.is_(None)
        ).first()

    def get_workout_templates(self, db: Session, *, trainer_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[WorkoutPlanTemplate]:
        return db.query(WorkoutPlanTemplate).filter(
            WorkoutPlanTemplate.trainer_id == trainer_id,
            WorkoutPlanTemplate.deleted_at.is_(None)
        ).order_by(WorkoutPlanTemplate.name).offset(skip).limit(limit).all()

    def update_workout_template(self, db: Session, *, template: WorkoutPlanTemplate, obj_in: WorkoutPlanTemplateUpdate) -> WorkoutPlanTemplate:
        """
        Updates an existing workout template.
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)
        db.add(template)
        db.commit()
        db.refresh(template)
        return template

    def delete_workout_template(self, db: Session, *, template: WorkoutPlanTemplate) -> None:
        """
        Soft deletes a workout template by setting the deleted_at timestamp.
        """
        template.deleted_at = datetime.utcnow()
        db.add(template)
        db.commit()
        return

    # --- Diet Plan Template Methods ---

    def create_diet_template(self, db: Session, *, obj_in: DietPlanTemplateCreate, trainer_id: uuid.UUID) -> DietPlanTemplate:
        db_obj = DietPlanTemplate(
            **obj_in.model_dump(),
            trainer_id=trainer_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def get_diet_template(self, db: Session, *, template_id: uuid.UUID, trainer_id: uuid.UUID) -> Optional[DietPlanTemplate]:
        """
        Retrieves a single diet template by its ID, ensuring it belongs to the specified trainer.
        """
        return db.query(DietPlanTemplate).filter(
            DietPlanTemplate.id == template_id,
            DietPlanTemplate.trainer_id == trainer_id,
            DietPlanTemplate.deleted_at.is_(None)
        ).first()

    def get_diet_templates(self, db: Session, *, trainer_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[DietPlanTemplate]:
        return db.query(DietPlanTemplate).filter(
            DietPlanTemplate.trainer_id == trainer_id,
            DietPlanTemplate.deleted_at.is_(None)
        ).order_by(DietPlanTemplate.name).offset(skip).limit(limit).all()

    def update_diet_template(self, db: Session, *, template: DietPlanTemplate, obj_in: DietPlanTemplateUpdate) -> DietPlanTemplate:
        """
        Updates an existing diet template.
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)
        db.add(template)
        db.commit()
        db.refresh(template)
        return template

    def delete_diet_template(self, db: Session, *, template: DietPlanTemplate) -> None:
        """
        Soft deletes a diet template by setting the deleted_at timestamp.
        """
        template.deleted_at = datetime.utcnow()
        db.add(template)
        db.commit()
        return

template_service = TemplateService()