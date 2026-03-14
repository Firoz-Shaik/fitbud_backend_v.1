# app/services/activity_feed_service.py
import uuid
from typing import List
from sqlalchemy.orm import Session
from app.models.activity import ActivityFeed
from app.domain.client_guards import assert_client_active
from app.models.client import Client
from fastapi import HTTPException, status

class ActivityFeedService:
    def get_activity_feed_for_client(self, db: Session, *, client_id: uuid.UUID, skip: int, limit: int) -> List[ActivityFeed]:
         # 1. Validate that the client exists and is active
        client = db.query(Client).filter(
            Client.id == client_id,
            Client.deleted_at.is_(None)
        ).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
        assert_client_active(client)
        
        # 2. Get the activity feed for the client
        return (
            db.query(ActivityFeed)
            .filter(ActivityFeed.client_id == client_id)
            .order_by(ActivityFeed.event_timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

activity_feed_service = ActivityFeedService()