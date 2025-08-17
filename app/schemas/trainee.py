# app/schemas/trainee.py
from pydantic import BaseModel
from typing import Any, Optional
from .assigned_plan import AssignedWorkoutPlan, AssignedDietPlan
from .core import CamelCaseModel
class TraineeToday(CamelCaseModel):
    assigned_workout: Any  # This will hold the workout JSON or be null
    is_rest_day: bool
    diet_compliance_percent: float
    current_streak_days: int
    is_fee_due: bool
class TraineePlans(CamelCaseModel):
    workout_plan: Optional[AssignedWorkoutPlan] = None
    diet_plan: Optional[AssignedDietPlan] = None