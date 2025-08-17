# app/api/v1/endpoints/logs.py
# API endpoints for clients to log workouts and meals.

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import CurrentUser, CurrentClient, DBSession
from app.models.user import User
from app.models.client import Client
from app.schemas.log import WorkoutLog, WorkoutLogCreate, DietLog, DietLogCreate
from app.services.log_service import log_service

router = APIRouter()

# --- Helper function for authorization ---
def authorize_log_access(db: DBSession, current_user: User, client_id: uuid.UUID):
    """
    Ensures the current user is authorized to view logs for the given client_id.
    - A client can only view their own logs.
    - A trainer can only view logs of their own clients.
    """
    if current_user.user_role == 'client':
        if not current_user.client_profile or current_user.client_profile.id != client_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view these logs.")
    elif current_user.user_role == 'trainer':
        client_record = db.query(Client).filter(Client.id == client_id, Client.trainer_user_id == current_user.id).first()
        if not client_record:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Client not found or not associated with this trainer.")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role not authorized.")

# --- Workout Log Routes ---

@router.post("/workout", response_model=WorkoutLog, status_code=status.HTTP_201_CREATED)
def create_workout_log(
    *,
    db: DBSession,
    log_in: WorkoutLogCreate,
    current_client: CurrentClient,
):
    """
    Log a workout session. (Client only)
    """
    if not current_client.client_profile:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client profile not found for this user.")
    log = log_service.create_workout_log(db=db, obj_in=log_in, client_id=current_client.client_profile.id)
    return log

@router.get("/workout", response_model=List[WorkoutLog])
def list_workout_logs(
    client_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve workout logs for a specific client.
    (Accessible by the client themselves or their trainer)
    """
    authorize_log_access(db, current_user, client_id)
    logs = log_service.get_workout_logs(db, client_id=client_id, start_date=start_date, end_date=end_date, skip=skip, limit=limit)
    return logs

# --- Diet Log Routes ---

@router.post("/diet", response_model=DietLog, status_code=status.HTTP_201_CREATED)
def create_diet_log(
    *,
    db: DBSession,
    log_in: DietLogCreate,
    current_client: CurrentClient,
):
    """
    Log a diet meal. (Client only)
    """
    if not current_client.client_profile:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client profile not found for this user.")
    log = log_service.create_diet_log(db=db, obj_in=log_in, client_id=current_client.client_profile.id)
    return log

@router.get("/diet", response_model=List[DietLog])
def list_diet_logs(
    client_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve diet logs for a specific client.
    (Accessible by the client themselves or their trainer)
    """
    authorize_log_access(db, current_user, client_id)
    logs = log_service.get_diet_logs(db, client_id=client_id, start_date=start_date, end_date=end_date, skip=skip, limit=limit)
    return logs
