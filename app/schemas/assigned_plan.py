# app/schemas/assigned_plan.py
# Pydantic models for assigning plans to clients.

import uuid
from typing import Any, Optional
from pydantic import BaseModel
from datetime import datetime
from .core import CamelCaseModel
from pydantic import computed_field
# --- Plan Assignment Schemas ---

class PlanAssignmentBase(CamelCaseModel):
    client_id: uuid.UUID
    source_template_id: uuid.UUID

class WorkoutPlanAssign(PlanAssignmentBase):
    pass

class DietPlanAssign(PlanAssignmentBase):
    pass

# --- Assigned Plan Response Schemas ---

class AssignedPlan(CamelCaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    source_template_id: uuid.UUID
    plan_details: Any # The JSONB snapshot
    assigned_at: datetime
    @computed_field
    @property
    def name(self) -> str:
        # Simply get the name from the planDetails dictionary
        return self.plan_details.get("name", "Custom Plan")
    
    class Config:
        from_attributes = True

class AssignedWorkoutPlan(AssignedPlan):
    pass

class AssignedDietPlan(AssignedPlan):
    pass
    
class ClientAssignedPlans(CamelCaseModel):
    latest_workout_plan: Optional[AssignedWorkoutPlan] = None
    latest_diet_plan: Optional[AssignedDietPlan] = None