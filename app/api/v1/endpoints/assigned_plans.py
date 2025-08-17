# app/api/v1/endpoints/assigned_plans.py
# API endpoints for trainers to assign plans to their clients.

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentTrainer, DBSession
from app.schemas.assigned_plan import (
    WorkoutPlanAssign, AssignedWorkoutPlan,
    DietPlanAssign, AssignedDietPlan
)
from app.services.assigned_plan_service import assigned_plan_service

router = APIRouter()

@router.post("/workout", response_model=AssignedWorkoutPlan, status_code=status.HTTP_201_CREATED)
def assign_workout_plan_to_client(
    *,
    db: DBSession,
    assignment_in: WorkoutPlanAssign,
    current_trainer: CurrentTrainer,
):
    """
    Assign a workout plan template to a client.
    
    This creates an immutable snapshot of the plan at the time of assignment.
    """
    assigned_plan = assigned_plan_service.assign_workout_plan(
        db=db, assignment_in=assignment_in, trainer_id=current_trainer.id
    )
    return assigned_plan

@router.post("/diet", response_model=AssignedDietPlan, status_code=status.HTTP_201_CREATED)
def assign_diet_plan_to_client(
    *,
    db: DBSession,
    assignment_in: DietPlanAssign,
    current_trainer: CurrentTrainer,
):
    """
    Assign a diet plan template to a client.

    This creates an immutable snapshot of the plan at the time of assignment.
    """
    assigned_plan = assigned_plan_service.assign_diet_plan(
        db=db, assignment_in=assignment_in, trainer_id=current_trainer.id
    )
    return assigned_plan
