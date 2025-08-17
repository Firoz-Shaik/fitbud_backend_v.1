# app/schemas/auth.py

from pydantic import BaseModel, EmailStr, constr
from .core import CamelCaseModel
class ClientRegister(CamelCaseModel):
    full_name: constr(min_length=1)
    email: EmailStr
    password: constr(min_length=8)
    invite_code: str