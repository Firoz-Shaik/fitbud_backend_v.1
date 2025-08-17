# app/services/client_service.py
# Contains the business logic for managing clients.
import uuid
import secrets
import string
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.log import Checkin
from sqlalchemy import desc
from app.models.client import Client
from app.models.user import User
from app.schemas.client import ClientInvite
from app.schemas.client import ClientUpdate
from pydantic import BaseModel
from app.models.plan import AssignedWorkoutPlan, AssignedDietPlan
from app.schemas.assigned_plan import ClientAssignedPlans

class ClientService:
    def update_client(self, db: Session, *, client: Client, obj_in: ClientUpdate) -> Client:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        db.add(client)
        db.commit()
        db.refresh(client)
        return client
    def generate_invite_code(self, length: int = 10) -> str:
        """Generates a cryptographically secure random string for invite codes."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(length))

    def get_client_by_id(self, db: Session, *, client_id: str, trainer_id: str) -> Optional[Client]:
        """
        Retrieves a single client by their ID, ensuring they belong to the specified trainer.
        It eagerly loads the associated user's data.
        """
        return (
            db.query(Client)
            .options(joinedload(Client.client_user)) # Eagerly load the user profile
            .filter(Client.id == client_id, Client.trainer_user_id == trainer_id, Client.deleted_at.is_(None))
            .first()
        )

    def get_clients_by_trainer(
        self, db: Session, *, trainer_id: str, status: Optional[str], skip: int = 0, limit: int = 100
    ) -> List[Client]:
        """
        Retrieves a list of clients for a given trainer, with optional status filtering.
        This query is optimized to use the 'clients_trainer_user_id_status_idx'.
        """
        query = (
            db.query(Client)
            .options(joinedload(Client.client_user))
            .filter(Client.trainer_user_id == trainer_id, Client.deleted_at.is_(None))
        )
        
        if status:
            query = query.filter(Client.status == status)
            
        return query.order_by(Client.created_at.desc()).offset(skip).limit(limit).all()

    def create_client_invite(self, db: Session, *, obj_in: ClientInvite, trainer_id: str) -> Client:
        """
        Creates a new client record with an 'invited' status and a unique invite code.
        This is the first step in onboarding a new client.
        """
        # First, check if a user with this email already exists and is a client for another trainer.
        existing_user_as_client = db.query(Client).join(User, Client.client_user_id == User.id).filter(User.email == obj_in.email).first()
        if existing_user_as_client:
            raise ValueError("This email is already registered as a client to a trainer.")

        invite_code = self.generate_invite_code()
        
        db_obj = Client(
            trainer_user_id=trainer_id,
            client_user_id=None,
            status='invited',
            goal=obj_in.goal, # Save to the new 'goal' field
            invite_code=invite_code,
            invited_full_name=obj_in.full_name, # NEW
            invited_email=obj_in.email,         # NEW
        )
        # Note: The client's full name from ClientInvite is used during the registration step,
        # not stored directly in the clients table. It will be part of the new User record.
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    def get_client_overview(self, db: Session, *, client_id: uuid.UUID, trainer_id: uuid.UUID) -> Optional[dict]:
        client = self.get_client_by_id(db, client_id=client_id, trainer_id=trainer_id)
        if not client:
            return None
        
        latest_checkin = db.query(Checkin).filter(Checkin.client_id == client_id).order_by(desc(Checkin.checked_in_at)).first()
        full_name = client.client_user.full_name if client.client_user else client.invited_full_name
        email = client.client_user.email if client.client_user else client.invited_email
        profile_photo_url = client.client_user.profile_photo_url if client.client_user else None

        return {
            "id": client.id,
            "full_name": full_name,
            "email": email,
            "profile_photo_url": profile_photo_url,
            "status": client.status,
            "goal": client.goal,
            "goal_description": client.goal_description,
            "current_weight_kg": float(latest_checkin.weight_kg) if latest_checkin and latest_checkin.weight_kg else client.initial_weight_kg,
            "height_cm": client.height_cm,
            "initial_weight_kg": client.initial_weight_kg,
            "invite_code": client.invite_code,
            "private_notes": client.private_notes,
            "health_notes": client.health_notes,
            "subscription_due_date": client.subscription_due_date,
            "subscription_paid_status": client.subscription_paid_status,
            "goal_weight_kg": None # Placeholder for V2
        }

    def update_client_notes(self, db: Session, *, client_id: uuid.UUID, trainer_id: uuid.UUID, notes: str) -> Client:
        client = self.get_client_by_id(db, client_id=client_id, trainer_id=trainer_id)
        if not client:
            raise ValueError("Client not found")
        
        client.private_notes = notes
        db.add(client)
        db.commit()
        db.refresh(client)
        return client
    def get_assigned_plans_for_client(self, db: Session, *, client_id: uuid.UUID) -> ClientAssignedPlans:
        """
        Retrieves the most recently assigned workout and diet plans for a specific client.
        """
        latest_workout_plan = (
            db.query(AssignedWorkoutPlan)
            .filter(AssignedWorkoutPlan.client_id == client_id, AssignedWorkoutPlan.deleted_at.is_(None))
            .order_by(AssignedWorkoutPlan.assigned_at.desc())
            .first()
        )

        latest_diet_plan = (
            db.query(AssignedDietPlan)
            .filter(AssignedDietPlan.client_id == client_id, AssignedDietPlan.deleted_at.is_(None))
            .order_by(AssignedDietPlan.assigned_at.desc())
            .first()
        )

        return ClientAssignedPlans(
            latest_workout_plan=latest_workout_plan,
            latest_diet_plan=latest_diet_plan,
        )

client_service = ClientService()
