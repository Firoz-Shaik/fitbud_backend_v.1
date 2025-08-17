# app/schemas/checkin.py
# Pydantic models for weekly check-ins.

import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, HttpUrl
from decimal import Decimal
from .core import CamelCaseModel
class CheckinCreate(CamelCaseModel):
    weight_kg: Optional[Decimal] = None
    # measurements can be any valid JSON, e.g., {"waist_cm": 80, "hip_cm": 95}
    measurements: Optional[Any] = None
    progress_photo_url: Optional[HttpUrl] = None
    # subjective_scores can be any valid JSON, e.g., {"energy": 8, "sleep_quality": 7}
    subjective_scores: Optional[Any] = None
    notes: Optional[str] = None

class Checkin(CamelCaseModel):
    id: int
    client_id: uuid.UUID
    weight_kg: Optional[Decimal] = None
    measurements: Optional[Any] = None
    progress_photo_url: Optional[str] = None
    subjective_scores: Optional[Any] = None
    notes: Optional[str] = None
    checked_in_at: datetime

    class Config:
        from_attributes = True
