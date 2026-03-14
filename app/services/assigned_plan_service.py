# app/services/assigned_plan_service.py
# V2 Business logic for assigning plans, using the new normalized structure.

import uuid
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.plan import AssignedWorkoutPlan, AssignedDietPlan
from app.schemas.assigned_plan import WorkoutPlanAssign, DietPlanAssign
from app.services.template_service import template_service
from app.domain.client_guards import assert_client_allows_action
from app.domain.authorization.client_access import get_client_for_trainer, get_client_for_viewer

class AssignedPlanService:
    def assign_workout_plan(self, db: Session, *, assignment_in: WorkoutPlanAssign, trainer_id: uuid.UUID) -> AssignedWorkoutPlan:
        """
        Assigns a workout plan to a client by building a complete JSON snapshot
        from the new normalized V2 template structure.
        """
        # 1. Validate that the client belong to the trainer
        client = get_client_for_trainer(
            db, 
            client_id=assignment_in.client_id, 
            trainer_id=trainer_id,
            )
        
        # 2. Validate that client is allowed to assign a plan
        assert_client_allows_action(client, "assign_workout")

        # 3. Validate that the template exists and belongs to the trainer
        template = template_service.get_workout_template(db, template_id=assignment_in.source_template_id, trainer_id=trainer_id)
        if not template:
            raise HTTPException(status_code=404, detail="Workout plan template not found.")

        # 4. Build the rich JSON snapshot from the template's relational items
        plan_snapshot = plan_snapshot = template_service.create_workout_plan_snapshot(template=template)

        # 5. Create the immutable assigned plan record
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
        # 1. Validate that the client belong to the trainer
        client = get_client_for_trainer(
            db, 
            client_id=assignment_in.client_id, 
            trainer_id=trainer_id,
            )
        
        # 2. Validate that the template exists and belongs to the trainer
        
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

    def list_assigned_workout_plans(
        self, db: Session, *, client_id: uuid.UUID, current_user
    ) -> List[AssignedWorkoutPlan]:
        """List assigned workout plans for a client. Authorization is enforced via get_client_for_viewer."""
        get_client_for_viewer(db, client_id=client_id, current_user=current_user)
        return (
            db.query(AssignedWorkoutPlan)
            .filter(
                AssignedWorkoutPlan.client_id == client_id,
                AssignedWorkoutPlan.deleted_at.is_(None),
            )
            .order_by(AssignedWorkoutPlan.assigned_at.desc())
            .all()
        )

    def list_assigned_diet_plans(
        self, db: Session, *, client_id: uuid.UUID, current_user
    ) -> List[AssignedDietPlan]:
        """List assigned diet plans for a client. Authorization is enforced via get_client_for_viewer."""
        get_client_for_viewer(db, client_id=client_id, current_user=current_user)
        return (
            db.query(AssignedDietPlan)
            .filter(
                AssignedDietPlan.client_id == client_id,
                AssignedDietPlan.deleted_at.is_(None),
            )
            .order_by(AssignedDietPlan.assigned_at.desc())
            .all()
        )

assigned_plan_service = AssignedPlanService()