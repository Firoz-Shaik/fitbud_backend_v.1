# app/services/checkin_service.py
# Business logic for creating and retrieving weekly check-ins.

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.api.deps import CurrentClient, CurrentUser
from app.domain.client_guards import assert_client_allows_action
from app.domain.authorization.client_access import get_client_for_viewer
from app.models.client import Client
from app.models.log import Checkin
from app.models.activity import ActivityFeed
from app.schemas.checkin import CheckinCreate

class CheckinService:
    def create_checkin(self, db: Session, *, obj_in: CheckinCreate, current_client: CurrentClient) -> Checkin:
        """
        Creates a weekly check-in and a corresponding activity feed entry in a single transaction.
        """
        # 1. Validate that the client exists and is active
        if not current_client.client_profile:
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST, 
             detail="Client profile not found for this user."
        )
        client_id = current_client.client_profile.id
        client = db.query(Client).filter(
            Client.id == client_id,
            Client.deleted_at.is_(None)
        ).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
        
        # 2. Validate that the client is allowed to check in
        assert_client_allows_action(client, "checkin")

        try:
            # 1. Create the check-in entry
            checkin_entry = Checkin(
                **obj_in.model_dump(),
                client_id=client_id
            )
            db.add(checkin_entry)
            
            # 2. Create the activity feed entry
            activity_metadata = {}
            if obj_in.weight_kg:
                activity_metadata["weight"] = f"{obj_in.weight_kg} kg"
            
            activity_entry = ActivityFeed(
                client_id=client_id,
                event_type='CHECKIN_SUBMITTED',
                event_timestamp=datetime.now(timezone.utc),
                event_metadata=activity_metadata
            )
            db.add(activity_entry)
            
            # 3. Commit the transaction
            db.commit()
            db.refresh(checkin_entry)
            return checkin_entry
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Failed to submit check-in: {e}"
            )

    def get_checkins_by_client(
        self, 
        db: Session, 
        *, 
        client_id: uuid.UUID, 
        current_user: CurrentUser,
        start_date: Optional[datetime], 
        end_date: Optional[datetime], 
        skip: int, 
        limit: int
    ) -> List[Checkin]:
        """
        Retrieves a list of check-ins for a specific client, with optional date filtering.
        """
        client = get_client_for_viewer(db, client_id=client_id, current_user=current_user)
        assert_client_allows_action(client, "view_checkins")

        query = db.query(Checkin).filter(Checkin.client_id == client_id)
        
        if start_date:
            query = query.filter(Checkin.checked_in_at >= start_date)
        if end_date:
            query = query.filter(Checkin.checked_in_at <= end_date)
            
        return query.order_by(Checkin.checked_in_at.desc()).offset(skip).limit(limit).all()

checkin_service = CheckinService()
