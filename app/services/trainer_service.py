# app/services/trainer_service.py
import uuid
from sqlalchemy.orm import Session
from app.models.client import Client
from datetime import date
from dateutil.relativedelta import relativedelta

class TrainerService:
    def get_trainer_stats(self, db: Session, *, trainer_id: uuid.UUID) -> dict:
        today = date.today()
        start_of_current_month = today.replace(day=1)

        current_active_clients = (
            db.query(Client)
            .filter(Client.trainer_user_id == trainer_id, Client.status == 'active', Client.deleted_at.is_(None))
            .count()
        )
        
        clients_at_start_of_month = (
            db.query(Client)
            .filter(
                Client.trainer_user_id == trainer_id, 
                Client.status == 'active', 
                Client.created_at < start_of_current_month,
                Client.deleted_at.is_(None)
            )
            .count()
        )
        
        growth_percentage = 0.0
        if clients_at_start_of_month > 0:
            growth = current_active_clients - clients_at_start_of_month
            growth_percentage = (growth / clients_at_start_of_month) * 100

        return {
            "active_clients": current_active_clients,
            "growth_percentage": round(growth_percentage, 2)
        }

trainer_service = TrainerService()