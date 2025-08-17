# app/api/v1/endpoints/checkins.py
# API endpoints for clients to submit weekly check-ins.

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import CurrentUser, CurrentClient, DBSession
# Re-using the authorization helper from the logging endpoints
from .logs import authorize_log_access 
from app.schemas.checkin import Checkin, CheckinCreate
from app.services.checkin_service import checkin_service

router = APIRouter()

@router.post("/", response_model=Checkin, status_code=status.HTTP_201_CREATED)
def submit_checkin(
    *,
    db: DBSession,
    checkin_in: CheckinCreate,
    current_client: CurrentClient,
):
    """
    Submit a weekly check-in. (Client only)
    """
    if not current_client.client_profile:
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST, 
             detail="Client profile not found for this user."
        )
    checkin = checkin_service.create_checkin(
        db=db, obj_in=checkin_in, client_id=current_client.client_profile.id
    )
    return checkin

@router.get("/", response_model=List[Checkin])
def list_checkins(
    client_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve check-ins for a specific client.
    (Accessible by the client themselves or their trainer)
    """
    # This helper function correctly checks if the current user is the client
    # or the client's assigned trainer.
    authorize_log_access(db, current_user, client_id)
    
    checkins = checkin_service.get_checkins_by_client(
        db, 
        client_id=client_id, 
        start_date=start_date, 
        end_date=end_date, 
        skip=skip, 
        limit=limit
    )
    return checkins
