# fitbud_v1/app/schemas/user.py

from typing import Optional
from pydantic import ConfigDict, EmailStr, constr, computed_field
import uuid
from datetime import datetime
from .core import CamelCaseModel

class UserBase(CamelCaseModel):
    email: EmailStr
    full_name: constr(min_length=1)

class UserCreate(UserBase):
    password: constr(min_length=8)
    user_role: str # 'trainer' or 'client'

class UserUpdate(CamelCaseModel):
    email: EmailStr | None = None
    full_name: constr(min_length=1) | None = None
    profile_photo_url: str | None = None

class User(UserBase):
    id: uuid.UUID
    full_name: Optional[str]
    user_role: str
    profile_photo_url: str | None = None
    created_at: Optional[datetime]
    @computed_field
    @property
    def client_profile_id(self) -> uuid.UUID | None:
        if hasattr(self, 'client_profile') and self.client_profile:
            return self.client_profile.id
        return None

    model_config = ConfigDict(from_attributes=True)
class UserPasswordUpdate(CamelCaseModel):
    current_password: str
    new_password: constr(min_length=8)

class UserEmailUpdate(CamelCaseModel):
    new_email: EmailStr
    password: str