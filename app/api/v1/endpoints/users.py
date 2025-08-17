# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends
from app.api.deps import CurrentUser, DBSession
from app.schemas.user import User, UserPasswordUpdate, UserEmailUpdate, UserUpdate
from app.services.user_service import user_service

router = APIRouter()

@router.get("/me", response_model=User)
def read_current_user(current_user: CurrentUser):
    """
    Get current user's profile.
    """
    return current_user

@router.put("/me", response_model=User)
def update_current_user_profile(
    profile_in: UserUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Update the current user's profile information.
    """
    user = user_service.update_user_profile(db=db, user=current_user, obj_in=profile_in)
    return user

@router.put("/me/password", response_model=User)
def change_user_password(
    password_in: UserPasswordUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Update the current user's password.
    """
    user = user_service.update_password(db=db, user=current_user, obj_in=password_in)
    return user

@router.put("/me/email", response_model=User)
def change_user_email(
    email_in: UserEmailUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Update the current user's email address.
    """
    user = user_service.update_email(db=db, user=current_user, obj_in=email_in)
    return user