# app/schemas/trainer.py
from pydantic import BaseModel, EmailStr, constr
from .core import CamelCaseModel

class TrainerStats(CamelCaseModel):
    active_clients: int
    growth_percentage: float

class TrainerCreate(CamelCaseModel):
    full_name: constr(min_length=1)
    email: EmailStr
    password: constr(min_length=8)
