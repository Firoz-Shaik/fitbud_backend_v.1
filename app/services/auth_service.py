# app/services/auth_service.py

from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.models.user import User
from app.services.user_service import user_service
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.core.config import settings
from app.core import security


class AuthService:
    def authenticate_user_for_token(
        self, db: Session, *, email: str, password: str
    ) -> User | None:
        """
        Authenticates a user by email and password.
        """
        user = user_service.get_user_by_email(db, email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials",
            )
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials",
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            user.email,
            expires_delta=access_token_expires,
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

auth_service = AuthService()
