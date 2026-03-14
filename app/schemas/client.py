# app/schemas/client.py
# Pydantic models for client data.

import uuid
from datetime import datetime,date
from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr, computed_field
from typing import Optional
from decimal import Decimal
from .user import User # Import User schema for nesting
from .core import CamelCaseModel

# Properties required when a trainer invites a new client.
class PaymentConfirmation(CamelCaseModel):
    is_confirmed: bool
    
class ClientInvite(CamelCaseModel):
    email: EmailStr
    full_name: constr(min_length=1)
    goal : str

# Properties of a client that can be updated.
class ClientUpdate(CamelCaseModel):
    client_status: Optional[str] = None
    goal: Optional[str] = None # Add this field
    goal_description: Optional[str] = None # Add this field
    private_notes: Optional[str] = None
    health_notes: Optional[str] = None
    subscription_due_date: Optional[datetime] = None
    subscription_paid_status: Optional[bool] = None
    initial_weight_kg: Optional[Decimal] = None
    height_cm: Optional[Decimal] = None


class ClientBase(CamelCaseModel):
    id: uuid.UUID
    client_status: str
    goal: Optional[str] = None 
    goal_description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class Client(ClientBase):
    # These are the raw fields from the database model
    trainer_user_id: uuid.UUID
    created_at: datetime
    client_user: Optional[User] = None
    invited_full_name: Optional[str] = None
    invited_email: Optional[EmailStr] = None
    invite_code: Optional[str] = None
    subscription_due_date: Optional[datetime] = None
    subscription_paid_status: Optional[bool] = None
    payment_status: Optional[str] = None
    private_notes: Optional[str] = None
    health_notes: Optional[str] = None

    @computed_field
    @property
    def is_fee_due(self) -> bool:
        """
        Returns True if the subscription is past its due date and not paid.
        """
        if self.subscription_due_date and self.subscription_paid_status is False:
            if date.today() >= self.subscription_due_date.date():
                return True
        return False
    # --- Computed fields for frontend compatibility ---
    @computed_field
    @property
    def name(self) -> str:
        # If the client has registered, use their real name.
        # Otherwise, use the name from the invitation.
        if self.client_user:
            return self.client_user.full_name
        return self.invited_full_name or "Invited Client"

    @computed_field
    @property
    def email(self) -> str:
        if self.client_user:
            return self.client_user.email
        return self.invited_email or ""

    @computed_field
    @property
    def profileImageUrl(self) -> Optional[str]:
        if self.client_user:
            return self.client_user.profile_photo_url
        return None

class ClientPrivateNotesUpdate(CamelCaseModel):
    private_notes: str

class ClientOverview(CamelCaseModel):
    id: uuid.UUID
    full_name: Optional[str] = None
    email: str
    profile_photo_url: Optional[str] = None
    # client_service.get_client_overview currently returns "status" key
    client_status: str = Field(validation_alias="status")
    goal: Optional[str] = None
    goal_description: Optional[str] = None
    current_weight_kg: Optional[float] = None
    height_cm: Optional[Decimal] = None
    initial_weight_kg: Optional[Decimal] = None
    current_weight_kg: Optional[Decimal] = None
    private_notes: Optional[str] = None
    invite_code: Optional[str] = None
    health_notes: Optional[str] = None
    subscription_due_date: Optional[datetime] = None
    subscription_paid_status: Optional[bool] = None
    payment_status: Optional[str] = None
    goal_weight_kg: Optional[float] = None

    @computed_field
    @property
    def is_fee_due(self) -> bool:
        """
        Returns True if the subscription is past its due date and not paid.
        """
        if self.subscription_due_date and self.subscription_paid_status is False:
            if date.today() >= self.subscription_due_date.date():
                return True
        return False     
