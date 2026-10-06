import os
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserProfileUpdate
from app.utils.security import (
    SECRET_KEY,
    ALGORITHM,
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def register_patient(arg1, arg2) -> User:
    """Supports both register_patient(db, user_data) and register_patient(user_data, db)."""
    if isinstance(arg1, Session):
        db = arg1
        user_data = arg2
    else:
        user_data = arg1
        db = arg2

    existing_user = db.query(User).filter(User.email == user_data.email.strip().lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered."
        )

    user = User(
        full_name=user_data.full_name.strip(),
        email=user_data.email.strip().lower(),
        phone=user_data.phone.strip(),
        password_hash=hash_password(user_data.password),
        age=user_data.age,
        gender=user_data.gender,
        role="PATIENT",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_patient(arg1, arg2, arg3=None) -> User:
    """
    Supports both:
    1. authenticate_patient(db, email, password)
    2. authenticate_patient(login_data, db)
    """
    if isinstance(arg1, Session):
        db = arg1
        email = arg2
        password = arg3
    elif isinstance(arg1, UserLogin):
        email = arg1.email
        password = arg1.password
        db = arg2
    else:
        email = str(arg1)
        password = str(arg2)
        db = arg3

    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email address or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact administrator.",
        )
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """FastAPI Dependency: Decodes JWT token and retrieves authenticated User."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    user_id_raw = payload.get("sub")
    if user_id_raw is None:
        raise credentials_exception

    try:
        user_id = int(user_id_raw)
    except ValueError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated",
        )
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI Dependency: Enforces ADMIN role-based access control."""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to access this resource."
        )
    return current_user

def update_patient_profile(user_id: int, profile_data: UserProfileUpdate, db: Session) -> User:
    """Updates optional health profile attributes for a patient."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found.")

    if profile_data.full_name is not None:
        user.full_name = profile_data.full_name.strip()
    if profile_data.phone is not None:
        user.phone = profile_data.phone.strip()
    if profile_data.age is not None:
        user.age = profile_data.age
    if profile_data.gender is not None:
        user.gender = profile_data.gender
    if profile_data.height is not None:
        user.height = profile_data.height
    if profile_data.weight is not None:
        user.weight = profile_data.weight
    if profile_data.blood_group is not None:
        user.blood_group = profile_data.blood_group
    if profile_data.allergies is not None:
        user.allergies = profile_data.allergies.strip() if profile_data.allergies else None
    if profile_data.existing_conditions is not None:
        user.existing_conditions = profile_data.existing_conditions.strip() if profile_data.existing_conditions else None

    db.commit()
    db.refresh(user)
    return user
