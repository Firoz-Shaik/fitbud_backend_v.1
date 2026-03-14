# app/api/v1/endpoints/trainees.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import CurrentUser, DBSession, CurrentClient
from app.schemas.trainee import TraineeToday
from app.services.trainee_service import trainee_service
from app.schemas.client import Client as ClientSchema
from app.models.client import Client as ClientModel
from app.schemas.trainee import TraineePlans

router = APIRouter()

@router.get("/me/today", response_model=TraineeToday)
def get_my_today_dashboard(
    db: DBSession,
    current_client: CurrentClient,
):
    """
    Get the main dashboard data for the currently authenticated client for 'Today'.
    """
    dashboard_data = trainee_service.get_trainee_dashboard(
        db=db,
        client_id=current_client.client_profile.id,
        current_user=current_client.user,
    )
    return dashboard_data

@router.get("/{trainee_id}/today", response_model=TraineeToday)
def get_trainee_today_dashboard(
    trainee_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser
):
    """
    Get the main dashboard data for a trainee for 'Today'.
    Accessible by the trainee themselves or their trainer.
    """
    # Authorization
    dashboard_data = trainee_service.get_trainee_dashboard(db=db, client_id=trainee_id, current_user=current_user)
    return dashboard_data
@router.get("/{trainee_id}/plans", response_model=TraineePlans)
def get_trainee_plans(
    trainee_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser
):
    """
    Get the currently assigned workout and diet plans for a trainee.
    Accessible by the trainee themselves or their trainer.
    """
    # Authorization
    plans = trainee_service.get_trainee_plans(db=db, client_id=trainee_id,current_user=current_user)
    return plans
@router.post("/me/mark-paid", response_model=ClientSchema)
def mark_my_fee_as_paid(
    db: DBSession,
    current_client: CurrentClient,
):
    """
    Allows the currently authenticated client to mark their fee as paid,
    setting the status to 'pending'.
    """
    updated_client = trainee_service.mark_payment_as_pending(db=db, current_client=current_client)
    return updated_client