# app/api/deps.py
# Contains FastAPI dependencies used across the application.

from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.core import security
from app.core.database import get_db
from app.models.user import User
from app.schemas.token import TokenData
from app.services.user_service import user_service

# This defines the security scheme for getting a bearer token.
# tokenUrl points to the endpoint where the client can fetch a token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get the current user from a JWT token.
    This will be used to protect endpoints.
    
    Raises:
        HTTPException: 401 Unauthorized if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(
            token, security.settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except (JWTError, ValidationError):
        raise credentials_exception
        
    user = user_service.get_user_by_email(db, email=token_data.email)
    if user is None or user.deleted_at is not None:
        raise credentials_exception
        
    return user

# Dependency to get the current active user with the 'trainer' role.
def get_current_active_trainer(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.user_role != "trainer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

# Dependency to get the current active user with the 'client' role.
def get_current_active_client(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.user_role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

# Type hints for dependencies to make router signatures cleaner
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentTrainer = Annotated[User, Depends(get_current_active_trainer)]
CurrentClient = Annotated[User, Depends(get_current_active_client)]
DBSession = Annotated[Session, Depends(get_db)]
