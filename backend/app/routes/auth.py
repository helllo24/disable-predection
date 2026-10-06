from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse, UserProfileUpdate
from app.services.auth_service import (
    register_patient,
    authenticate_patient,
    get_current_user,
    update_patient_profile
)
from app.utils.security import create_access_token
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication & Profile"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registers a new patient."""
    user = register_patient(db, user_data)
    return user

@router.post("/login", response_model=TokenResponse)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticates patient email/password and returns a JWT token."""
    user = authenticate_patient(db, user_credentials.email, user_credentials.password)
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the authenticated patient's profile details."""
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates the authenticated patient's profile information."""
    updated_user = update_patient_profile(
        user_id=current_user.id,
        profile_data=profile_data,
        db=db
    )
    return updated_user

@router.post("/logout")
def logout():
    """Logs out the user session."""
    return {"message": "Logged out successfully"}
