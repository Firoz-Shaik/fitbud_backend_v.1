# app/schemas/assigned_plan.py
# Pydantic models for assigning plans to clients.

import uuid
from typing import Any, Optional
from pydantic import BaseModel, computed_field
from datetime import datetime
from .core import CamelCaseModel
# No longer imports from .template, fixing the ImportError

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
    plan_details: Any # The JSONB snapshot created by the service
    assigned_at: datetime
    
    @computed_field
    @property
    def name(self) -> str:
        if isinstance(self.plan_details, dict) and "name" in self.plan_details:
            return self.plan_details["name"]
        return "Custom Plan"
    
    class Config:
        from_attributes = True

class AssignedWorkoutPlan(AssignedPlan):
    pass

class AssignedDietPlan(AssignedPlan):
    pass
    
class ClientAssignedPlans(CamelCaseModel):
    latest_workout_plan: Optional[AssignedWorkoutPlan] = None
    latest_diet_plan: Optional[AssignedDietPlan] = None

    @computed_field
    @property
    def latestWorkoutPlan(self) -> Optional[AssignedWorkoutPlan]:
        return self.latest_workout_plan

    @computed_field
    @property
    def latestDietPlan(self) -> Optional[AssignedDietPlan]:
        return self.latest_diet_plan