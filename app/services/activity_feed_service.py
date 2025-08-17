# app/services/activity_feed_service.py
import uuid
from typing import List
from sqlalchemy.orm import Session
from app.models.activity import ActivityFeed

class ActivityFeedService:
    def get_activity_feed_for_client(self, db: Session, *, client_id: uuid.UUID, skip: int, limit: int) -> List[ActivityFeed]:
        return (
            db.query(ActivityFeed)
            .filter(ActivityFeed.client_id == client_id)
            .order_by(ActivityFeed.event_timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

activity_feed_service = ActivityFeedService()