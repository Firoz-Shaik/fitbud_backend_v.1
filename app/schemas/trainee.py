# app/schemas/trainee.py
from pydantic import BaseModel, computed_field
from typing import Any, Optional
from datetime import datetime
from .assigned_plan import AssignedWorkoutPlan, AssignedDietPlan
from .core import CamelCaseModel
class TraineeToday(CamelCaseModel):
    assigned_workout: Any  # This will hold the workout JSON or be null
    is_rest_day: bool
    diet_compliance_percent: float
    current_streak_days: int
    is_fee_due: bool
    payment_status: Optional[str] = None
    subscription_due_date: Optional[datetime] = None

    @computed_field
    @property
    def subscriptionDueDate(self) -> Optional[datetime]:
        return self.subscription_due_date
    
class TraineePlans(CamelCaseModel):
    workout_plan: Optional[AssignedWorkoutPlan] = None
    diet_plan: Optional[AssignedDietPlan] = None