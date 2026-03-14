# app/api/v1/endpoints/assigned_plans.py
# API endpoints for trainers to assign plans to their clients.

import uuid
from typing import List
from fastapi import APIRouter, Query, status

from app.api.deps import CurrentTrainer, CurrentUser, DBSession
from app.schemas.assigned_plan import (
    WorkoutPlanAssign, AssignedWorkoutPlan,
    DietPlanAssign, AssignedDietPlan
)
from app.services.assigned_plan_service import assigned_plan_service

router = APIRouter()


@router.get("/workout", response_model=List[AssignedWorkoutPlan])
def list_assigned_workout_plans(
    db: DBSession,
    current_user: CurrentUser,
    client_id: uuid.UUID = Query(..., description="Client ID to list plans for"),
):
    """
    List assigned workout plans for a client.
    Accessible by the trainer (if they own the client) or the client themselves.
    Authorization is enforced in the service layer.
    """
    return assigned_plan_service.list_assigned_workout_plans(
        db=db, client_id=client_id, current_user=current_user
    )


@router.get("/diet", response_model=List[AssignedDietPlan])
def list_assigned_diet_plans(
    db: DBSession,
    current_user: CurrentUser,
    client_id: uuid.UUID = Query(..., description="Client ID to list plans for"),
):
    """
    List assigned diet plans for a client.
    Accessible by the trainer (if they own the client) or the client themselves.
    Authorization is enforced in the service layer.
    """
    return assigned_plan_service.list_assigned_diet_plans(
        db=db, client_id=client_id, current_user=current_user
    )


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
