# app/services/checkin_service.py
# Business logic for creating and retrieving weekly check-ins.

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.log import Checkin
from app.models.activity import ActivityFeed
from app.schemas.checkin import CheckinCreate

class CheckinService:
    def create_checkin(self, db: Session, *, obj_in: CheckinCreate, client_id: uuid.UUID) -> Checkin:
        """
        Creates a weekly check-in and a corresponding activity feed entry in a single transaction.
        """
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
                event_timestamp=datetime.utcnow(),
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
        start_date: Optional[datetime], 
        end_date: Optional[datetime], 
        skip: int, 
        limit: int
    ) -> List[Checkin]:
        """
        Retrieves a list of check-ins for a specific client, with optional date filtering.
        """
        query = db.query(Checkin).filter(Checkin.client_id == client_id)
        
        if start_date:
            query = query.filter(Checkin.checked_in_at >= start_date)
        if end_date:
            query = query.filter(Checkin.checked_in_at <= end_date)
            
        return query.order_by(Checkin.checked_in_at.desc()).offset(skip).limit(limit).all()

checkin_service = CheckinService()
