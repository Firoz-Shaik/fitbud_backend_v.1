# app/api/v1/endpoints/auth.py

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core import security
from app.core.config import settings
from app.services.auth_service import auth_service
from app.services.user_service import user_service
from app.schemas.token import Token
# CORRECTED: Import UserCreate alongside User
from app.schemas.user import User, UserCreate
from app.schemas.auth import ClientRegister
from app.models.client import Client
from app.api.deps import get_current_user, DBSession, CurrentUser

router = APIRouter()

@router.post("/token", response_model=Token)
def login_for_access_token(
    db: DBSession, form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = auth_service.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.email, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register/client", response_model=User)
def register_client(
    *,
    db: DBSession,
    client_in: ClientRegister,
) -> Any:
    """
    Register a new client using an invite code.
    This is a transactional operation.
    """
    # 1. Check if a user with this email already exists
    existing_user = user_service.get_user_by_email(db, email=client_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists in the system.",
        )

    # 2. Find the client invitation
    client_record = db.query(Client).filter(Client.invite_code == client_in.invite_code).first()

    if not client_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The invite code is invalid or has expired.",
        )
    
    if client_record.status != 'invited':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invite has already been used or is inactive.",
        )

    try:
        # 3. Create the user record for the client
        # CORRECTED: Create a proper UserCreate object before passing to the service
        user_to_create = UserCreate(
            email=client_in.email,
            password=client_in.password,
            full_name=client_in.full_name,
            user_role="client"
        )
        new_user = user_service.create_user(db, obj_in=user_to_create)
        
        # 4. Update the client record with the new user's ID and set to active
        client_record.client_user_id = new_user.id
        client_record.status = 'active'
        db.add(client_record)
        
        db.commit()
        db.refresh(new_user)
        return new_user

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {e}",
        )

