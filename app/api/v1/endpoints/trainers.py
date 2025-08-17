# app/api/v1/endpoints/trainers.py
import uuid
from fastapi import APIRouter, Depends
from app.api.deps import CurrentTrainer, DBSession
from app.schemas.trainer import TrainerStats
from app.services.trainer_service import trainer_service

router = APIRouter()

@router.get("/me/stats", response_model=TrainerStats)
def get_my_stats(
    db: DBSession,
    current_trainer: CurrentTrainer,
):
    """
    Get statistics for the currently authenticated trainer.
    """
    stats = trainer_service.get_trainer_stats(db=db, trainer_id=current_trainer.id)
    return stats