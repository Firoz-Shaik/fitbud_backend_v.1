# app/api/v1/endpoints/trainees.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import CurrentUser, DBSession
from app.schemas.trainee import TraineeToday
from app.services.trainee_service import trainee_service
from app.models.client import Client
from app.schemas.trainee import TraineePlans

router = APIRouter()

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
    if current_user.user_role == 'client':
        if not current_user.client_profile or current_user.client_profile.id != trainee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    elif current_user.user_role == 'trainer':
        client = db.query(Client).filter(Client.id == trainee_id, Client.trainer_user_id == current_user.id).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found for this trainer")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
    dashboard_data = trainee_service.get_trainee_dashboard(db=db, client_id=trainee_id)
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
    if current_user.user_role == 'client':
        if not current_user.client_profile or current_user.client_profile.id != trainee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    elif current_user.user_role == 'trainer':
        client = db.query(Client).filter(Client.id == trainee_id, Client.trainer_user_id == current_user.id).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found for this trainer")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    plans = trainee_service.get_trainee_plans(db=db, client_id=trainee_id)
    return plans