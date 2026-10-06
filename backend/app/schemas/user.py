from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255, description="Full Name of the patient")
    email: EmailStr = Field(..., description="Valid Email address")
    phone: str = Field(..., min_length=7, max_length=20, description="Contact phone number")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    confirm_password: str = Field(..., description="Confirm password")
    age: int = Field(..., gt=0, lt=120, description="Age of the patient")
    gender: str = Field(..., description="Gender (Male, Female, Other)")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        valid_genders = ["male", "female", "other"]
        if v.lower().strip() not in valid_genders:
            raise ValueError("Gender must be Male, Female, or Other")
        return v.capitalize()

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Registered Email address")
    password: str = Field(..., description="Password")

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, min_length=7, max_length=20)
    age: Optional[int] = Field(None, gt=0, lt=120)
    gender: Optional[str] = None
    height: Optional[float] = Field(None, gt=0, lt=300, description="Height in cm")
    weight: Optional[float] = Field(None, gt=0, lt=500, description="Weight in kg")
    blood_group: Optional[str] = Field(None, description="Blood Group e.g. A+, O-")
    allergies: Optional[str] = Field(None, description="Known allergies")
    existing_conditions: Optional[str] = Field(None, description="Pre-existing medical conditions")

    @field_validator("gender")
    @classmethod
    def validate_gender_optional(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid_genders = ["male", "female", "other"]
            if v.lower().strip() not in valid_genders:
                raise ValueError("Gender must be Male, Female, or Other")
            return v.capitalize()
        return v

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    age: int
    gender: str
    role: str
    height: Optional[float] = None
    weight: Optional[float] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    existing_conditions: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
