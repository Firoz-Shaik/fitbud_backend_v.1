# app/api/v1/endpoints/clients.py
# API endpoints for trainers to manage their clients.

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.schemas.client import ClientOverview, ClientPrivateNotesUpdate
from app.schemas.activity import ActivityFeedItem
from app.services.activity_feed_service import activity_feed_service
from app.api.deps import CurrentTrainer, DBSession
from app.schemas.client import Client, ClientInvite
from app.services.client_service import client_service
from app.schemas.client import ClientUpdate
from app.schemas.assigned_plan import ClientAssignedPlans

router = APIRouter()

@router.get("/", response_model=List[Client])
def read_clients(
    db: DBSession,
    current_trainer: CurrentTrainer,
    status: Optional[str] = Query(None, enum=["invited", "active", "inactive"]),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve a list of clients for the currently authenticated trainer.
    Can be filtered by status.
    """
    clients = client_service.get_clients_by_trainer(
        db, trainer_id=current_trainer.id, status=status, skip=skip, limit=limit
    )
    return clients

@router.post("/", response_model=Client, status_code=status.HTTP_201_CREATED)
def invite_client(
    *,
    db: DBSession,
    client_in: ClientInvite,
    current_trainer: CurrentTrainer,
):
    """
    Invite a new client. This creates a client record with 'invited' status
    and generates a unique invite code.
    """
    try:
        client = client_service.create_client_invite(
            db=db, obj_in=client_in, trainer_id=current_trainer.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return client

@router.get("/{client_id}", response_model=Client)
def read_client(
    client_id: uuid.UUID,
    db: DBSession,
    current_trainer: CurrentTrainer,
):
    """
    Get a specific client by ID.
    """
    client = client_service.get_client_by_id(
        db, client_id=client_id, trainer_id=current_trainer.id
    )
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )
    return client
@router.get("/{client_id}/overview", response_model=ClientOverview)
def get_client_overview(
    client_id: uuid.UUID,
    db: DBSession,
    current_trainer: CurrentTrainer,
):
    """
    Get a rich overview of a specific client.
    """
    overview = client_service.get_client_overview(db=db, client_id=client_id, trainer_id=current_trainer.id)
    if not overview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return overview

@router.get("/{client_id}/activity-feed", response_model=List[ActivityFeedItem])
def get_client_activity_feed(
    client_id: uuid.UUID,
    db: DBSession,
    current_trainer: CurrentTrainer,
    skip: int = 0,
    limit: int = 50,
):
    """
    Get the activity feed for a specific client.
    """
    # Authorization check
    client = client_service.get_client_by_id(db, client_id=client_id, trainer_id=current_trainer.id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    
    feed = activity_feed_service.get_activity_feed_for_client(db=db, client_id=client_id, skip=skip, limit=limit)
    return feed

@router.patch("/{client_id}/notes", response_model=Client)
def update_client_private_notes(
    client_id: uuid.UUID,
    notes_in: ClientPrivateNotesUpdate,
    db: DBSession,
    current_trainer: CurrentTrainer,
):
    """
    Update the private notes for a specific client.
    """
    try:
        client = client_service.update_client_notes(
            db=db, client_id=client_id, trainer_id=current_trainer.id, notes=notes_in.private_notes
        )
        return client
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

# Note: Endpoints for GET /clients/{client_id}/activity_feed and PATCH for status
# will be added in subsequent phases as per the design document. This covers the
# core GET list and POST invite flows.

@router.patch("/{client_id}", response_model=Client)
def update_client_details(
    client_id: uuid.UUID,
    client_in: ClientUpdate,
    db: DBSession,
    current_trainer: CurrentTrainer,
):
    """
    Update details for a specific client. (Trainer only)
    """
    client = client_service.get_client_by_id(db, client_id=client_id, trainer_id=current_trainer.id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    
    updated_client = client_service.update_client(db=db, client=client, obj_in=client_in)
    return updated_client

@router.get("/{client_id}/assigned-plans", response_model=ClientAssignedPlans)
def get_client_assigned_plans(
    client_id: uuid.UUID,
    db: DBSession,
    current_trainer: CurrentTrainer,
):
    """
    Retrieve the latest assigned workout and diet plans for a specific client.
    """
    # Authorization check to ensure the client belongs to the trainer
    client = client_service.get_client_by_id(db, client_id=client_id, trainer_id=current_trainer.id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )

    plans = client_service.get_assigned_plans_for_client(db=db, client_id=client_id)
    return plans