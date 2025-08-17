# app/services/auth_service.py

from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.models.user import User
from app.services.user_service import user_service

class AuthService:
    def authenticate_user(
        self, db: Session, *, email: str, password: str
    ) -> User | None:
        """
        Authenticates a user by email and password.
        """
        user = user_service.get_user_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

auth_service = AuthService()