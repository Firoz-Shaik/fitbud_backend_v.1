# app/schemas/log.py
# Pydantic models for workout and diet logs.

import uuid
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, constr
from .core import CamelCaseModel

# --- Workout Log Schemas ---

class WorkoutLogCreate(CamelCaseModel):
    assigned_plan_id: uuid.UUID
    # The performance_data can be any valid JSON structure.
    # The frontend will be responsible for its shape.
    performance_data: Any 

class WorkoutLog(CamelCaseModel):
    id: int
    client_id: uuid.UUID
    assigned_plan_id: uuid.UUID
    performance_data: Any
    logged_at: datetime

    class Config:
        from_attributes = True

# --- Diet Log Schemas ---

class DietLogCreate(CamelCaseModel):
    assigned_plan_id: uuid.UUID
    meal_name: constr(min_length=1)
    status: str # Must be one of 'Followed', 'Partially Followed', 'Skipped'

class DietLog(CamelCaseModel):
    id: int
    client_id: uuid.UUID
    assigned_plan_id: uuid.UUID
    meal_name: str
    status: str
    logged_at: datetime

    class Config:
        from_attributes = True
