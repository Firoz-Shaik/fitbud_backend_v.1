# fitbud_v1/app/schemas/user.py

from pydantic import BaseModel, EmailStr, constr
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
    user_role: str
    profile_photo_url: str | None = None
    created_at: datetime

    class Config:
        # This allows Pydantic to create the model from an ORM object
        from_attributes = True
class UserPasswordUpdate(CamelCaseModel):
    current_password: str
    new_password: constr(min_length=8)

class UserEmailUpdate(CamelCaseModel):
    new_email: EmailStr
    password: str