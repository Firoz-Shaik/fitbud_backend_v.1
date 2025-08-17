# app/schemas/activity.py
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel
from .core import CamelCaseModel

class ActivityFeedItem(CamelCaseModel):
    id: int
    event_type: str
    event_timestamp: datetime
    event_metadata: Any

    class Config:
        from_attributes = True