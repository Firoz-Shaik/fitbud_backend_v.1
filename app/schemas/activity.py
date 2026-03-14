# app/schemas/activity.py
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from .core import CamelCaseModel

class ActivityFeedItem(CamelCaseModel):
    id: int
    event_type: str
    event_timestamp: datetime
    event_metadata: Any = Field(alias="event_metadata")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)