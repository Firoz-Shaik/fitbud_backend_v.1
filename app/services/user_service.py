# app/services/user_service.py
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserPasswordUpdate, UserEmailUpdate
from app.schemas.user import UserCreate, UserPasswordUpdate, UserEmailUpdate, UserUpdate

class UserService:
    # --- THIS METHOD WAS MISSING ---
    def get_user_by_email(self, db: Session, *, email: str) -> User | None:
        return (
        db.query(User)
        .options(joinedload(User.client_profile))
        .filter(User.email == email, User.deleted_at.is_(None))
        .first()
    )
    def create_user(self, db: Session, *, obj_in: UserCreate) -> User:
        hashed_password = get_password_hash(obj_in.password)
        db_obj = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
            user_role=obj_in.user_role,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_password(self, db: Session, *, user: User, obj_in: UserPasswordUpdate) -> User:
        if not verify_password(obj_in.current_password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")
        
        user.hashed_password = get_password_hash(obj_in.new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_email(self, db: Session, *, user: User, obj_in: UserEmailUpdate) -> User:
        if not verify_password(obj_in.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
        
        existing_user = self.get_user_by_email(db, email=obj_in.new_email)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
            
        user.email = obj_in.new_email
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def update_user_profile(self, db: Session, *, user: User, obj_in: UserUpdate) -> User:
        """
        Updates a user's profile information (full_name, profile_photo_url).
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

user_service = UserService()