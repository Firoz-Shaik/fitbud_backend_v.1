# app/services/assigned_plan_service.py
# Business logic for assigning workout and diet plans to clients.

import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.client import Client
from app.models.template import WorkoutPlanTemplate, DietPlanTemplate
from app.models.plan import AssignedWorkoutPlan, AssignedDietPlan
from app.schemas.assigned_plan import WorkoutPlanAssign, DietPlanAssign

class AssignedPlanService:
    def assign_workout_plan(self, db: Session, *, assignment_in: WorkoutPlanAssign, trainer_id: uuid.UUID) -> AssignedWorkoutPlan:
        """
        Assigns a workout plan to a client, creating an immutable snapshot.
        """
        # 1. Validate that the client belongs to the trainer
        client = db.query(Client).filter(
            Client.id == assignment_in.client_id,
            Client.trainer_user_id == trainer_id,
            Client.deleted_at.is_(None)
        ).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found or does not belong to this trainer.")

        # 2. Validate that the template belongs to the trainer
        template = db.query(WorkoutPlanTemplate).filter(
            WorkoutPlanTemplate.id == assignment_in.source_template_id,
            WorkoutPlanTemplate.trainer_id == trainer_id,
            WorkoutPlanTemplate.deleted_at.is_(None)
        ).first()
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout plan template not found or does not belong to this trainer.")
        plan_snapshot = {
            "name": template.name,
            "plan_structure": template.plan_structure
        }

        # 3. Create the immutable snapshot
        db_obj = AssignedWorkoutPlan(
            client_id=assignment_in.client_id,
            source_template_id=assignment_in.source_template_id,
            plan_details=plan_snapshot, # This is the critical snapshot step
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def assign_diet_plan(self, db: Session, *, assignment_in: DietPlanAssign, trainer_id: uuid.UUID) -> AssignedDietPlan:
        """
        Assigns a diet plan to a client, creating an immutable snapshot.
        """
        # 1. Validate client
        client = db.query(Client).filter(
            Client.id == assignment_in.client_id,
            Client.trainer_user_id == trainer_id,
            Client.deleted_at.is_(None)
        ).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found or does not belong to this trainer.")
        
        # 2. Validate template
        template = db.query(DietPlanTemplate).filter(
            DietPlanTemplate.id == assignment_in.source_template_id,
            DietPlanTemplate.trainer_id == trainer_id,
            DietPlanTemplate.deleted_at.is_(None)
        ).first()
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diet plan template not found or does not belong to this trainer.")
        
        plan_snapshot = {
            "name": template.name,
            "plan_structure": template.plan_structure
        }
        # 3. Create snapshot
        db_obj = AssignedDietPlan(
            client_id=assignment_in.client_id,
            source_template_id=assignment_in.source_template_id,
            plan_details=plan_snapshot,
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

assigned_plan_service = AssignedPlanService()
