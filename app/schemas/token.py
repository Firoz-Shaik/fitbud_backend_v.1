# fitbud_v1/app/schemas/token.py

from pydantic import BaseModel, EmailStr
from .core import CamelCaseModel
class Token(CamelCaseModel):
    access_token: str
    token_type: str

class TokenData(CamelCaseModel):
    email: EmailStr | None = None