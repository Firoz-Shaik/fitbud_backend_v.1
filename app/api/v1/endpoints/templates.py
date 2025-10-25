# app/api/v1/endpoints/templates.py
# API endpoints for trainers to manage their plan templates.

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query

from app.api.deps import CurrentTrainer, DBSession
from app.schemas.template import (
    WorkoutPlanTemplate, WorkoutPlanTemplateCreate, WorkoutPlanTemplateUpdate,
    DietPlanTemplate, DietPlanTemplateCreate, DietPlanTemplateUpdate
)
from app.services.template_service import template_service

router = APIRouter()

# --- Workout Plan Template Routes ---

@router.post("/workout", response_model=WorkoutPlanTemplate, status_code=status.HTTP_201_CREATED)
def create_workout_template(
    *,
    db: DBSession,
    template_in: WorkoutPlanTemplateCreate,
    current_trainer: CurrentTrainer,
):
    """
    Create a new workout plan template.
    """
    template = template_service.create_workout_template(
        db=db, obj_in=template_in, trainer_id=current_trainer.id
    )
    return template

@router.get("/workout", response_model=List[WorkoutPlanTemplate])
def list_workout_templates(
    db: DBSession,
    current_trainer: CurrentTrainer,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """
    Retrieve workout plan templates for the current trainer.
    """
    templates = template_service.get_workout_templates(
        db=db, trainer_id=current_trainer.id, skip=skip, limit=limit
    )
    return templates

@router.get("/workout/{template_id}", response_model=WorkoutPlanTemplate)
def get_workout_template(
    template_id: uuid.UUID,
    db: DBSession,
    current_trainer: CurrentTrainer,
):
    """
    Retrieve a single workout template by ID.
    """
    template = template_service.get_workout_template(db=db, template_id=template_id, trainer_id=current_trainer.id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout template not found")
    return template

@router.put("/workout/{template_id}", response_model=WorkoutPlanTemplate)
def update_workout_template(
    template_id: uuid.UUID,
    template_in: WorkoutPlanTemplateUpdate,
    db: DBSession,
    current_trainer: CurrentTrainer,
):
    """
    Update a workout template.
    """
    template = template_service.get_workout_template(db=db, template_id=template_id, trainer_id=current_trainer.id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout template not found")
    
    updated_template = template_service.update_workout_template(db=db, template=template, obj_in=template_in)
    return updated_template

@router.delete("/workout/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout_template(
    template_id: uuid.UUID,
    db: DBSession,
    current_trainer: CurrentTrainer,
):
    """
    Delete a workout template.
    """
    template = template_service.get_workout_template(db=db, template_id=template_id, trainer_id=current_trainer.id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout template not found")
    
    template_service.delete_workout_template(db=db, template=template)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Diet Plan Template Routes ---

@router.post("/diet", response_model=DietPlanTemplate, status_code=status.HTTP_201_CREATED)
def create_diet_template(
    *,
    db: DBSession,
    template_in: DietPlanTemplateCreate,
    current_trainer: CurrentTrainer,
):
    """
    Create a new diet plan template.
    """
    template = template_service.create_diet_template(
        db=db, obj_in=template_in, trainer_id=current_trainer.id
    )
    return template

@router.get("/diet", response_model=List[DietPlanTemplate])
def list_diet_templates(
    db: DBSession,
    current_trainer: CurrentTrainer,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """
    Retrieve diet plan templates for the current trainer.
    """
    templates = template_service.get_diet_templates(
        db=db, trainer_id=current_trainer.id, skip=skip, limit=limit
    )
    return templates

@router.get("/diet/{template_id}", response_model=DietPlanTemplate)
def get_diet_template(
    template_id: uuid.UUID,
    db: DBSession,
    current_trainer: CurrentTrainer,
):
    """
    Retrieve a single diet template by ID.
    """
    template = template_service.get_diet_template(db=db, template_id=template_id, trainer_id=current_trainer.id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diet template not found")
    return template

@router.put("/diet/{template_id}", response_model=DietPlanTemplate)
def update_diet_template(
    template_id: uuid.UUID,
    template_in: DietPlanTemplateUpdate,
    db: DBSession,
    current_trainer: CurrentTrainer,
):
    """
    Update a diet template.
    """
    template = template_service.get_diet_template(db=db, template_id=template_id, trainer_id=current_trainer.id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diet template not found")
    
    updated_template = template_service.update_diet_template(db=db, template=template, obj_in=template_in)
    return updated_template

@router.delete("/diet/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diet_template(
    template_id: uuid.UUID,
    db: DBSession,
    current_trainer: CurrentTrainer,
):
    """
    Delete a diet template.
    """
    template = template_service.get_diet_template(db=db, template_id=template_id, trainer_id=current_trainer.id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diet template not found")
    
    template_service.delete_diet_template(db=db, template=template)
    return Response(status_code=status.HTTP_204_NO_CONTENT)