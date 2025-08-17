# app/schemas/trainer.py
from pydantic import BaseModel
from .core import CamelCaseModel
class TrainerStats(CamelCaseModel):
    active_clients: int
    growth_percentage: float