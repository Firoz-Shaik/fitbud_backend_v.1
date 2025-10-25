# app/services/assigned_plan_service.py
# V2 Business logic for assigning plans, using the new normalized structure.

import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.client import Client
from app.models.template import WorkoutPlanTemplate, DietPlanTemplate
from app.models.plan import AssignedWorkoutPlan, AssignedDietPlan
from app.schemas.assigned_plan import WorkoutPlanAssign, DietPlanAssign
from app.services.template_service import template_service # Import the template service

class AssignedPlanService:
    def assign_workout_plan(self, db: Session, *, assignment_in: WorkoutPlanAssign, trainer_id: uuid.UUID) -> AssignedWorkoutPlan:
        """
        Assigns a workout plan to a client by building a complete JSON snapshot
        from the new normalized V2 template structure.
        """
        # 1. Validate that the client and template exist and belong to the trainer
        client = db.query(Client).filter(Client.id == assignment_in.client_id, Client.trainer_user_id == trainer_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found.")

        template = template_service.get_workout_template(db, template_id=assignment_in.source_template_id, trainer_id=trainer_id)
        if not template:
            raise HTTPException(status_code=404, detail="Workout plan template not found.")

        # 2. Build the rich JSON snapshot from the template's relational items
        plan_snapshot = plan_snapshot = template_service.create_workout_plan_snapshot(template=template)

        # 3. Create the immutable assigned plan record
        db_obj = AssignedWorkoutPlan(
            client_id=assignment_in.client_id,
            source_template_id=assignment_in.source_template_id,
            plan_details=plan_snapshot,
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def assign_diet_plan(self, db: Session, *, assignment_in: DietPlanAssign, trainer_id: uuid.UUID) -> AssignedDietPlan:
        """
        Assigns a diet plan by building a JSON snapshot from the V2 structure.
        """
        client = db.query(Client).filter(Client.id == assignment_in.client_id, Client.trainer_user_id == trainer_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found.")

        template = template_service.get_diet_template(db, template_id=assignment_in.source_template_id, trainer_id=trainer_id)
        if not template:
            raise HTTPException(status_code=404, detail="Diet plan template not found.")

        # Build the snapshot from the new structure
        plan_snapshot = plan_snapshot = template_service.create_diet_plan_snapshot(template=template)

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