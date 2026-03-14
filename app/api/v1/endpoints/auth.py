# app/api/v1/endpoints/auth.py

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core import security
from app.core.config import settings
from app.services.auth_service import auth_service
from app.services.user_service import user_service
from app.services.client_service import client_service
from app.schemas.token import Token
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
    return auth_service.authenticate_user_for_token(
        db, email=form_data.username, password=form_data.password
    )

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
    return client_service.register_client_user_by_invite_code(
        db=db, client_in=client_in
    )


@router.get("/users/me", response_model=User)
def read_users_me(current_user: CurrentUser) -> Any:
    """
    Get current user's profile.
    """
    return current_user
