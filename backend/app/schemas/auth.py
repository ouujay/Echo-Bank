"""
Authentication Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=6)
    pin: str = Field(..., min_length=4, max_length=4, pattern="^[0-9]{4}$")
    bvn: Optional[str] = Field(None, min_length=11, max_length=11)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class PINVerification(BaseModel):
    """Schema for PIN verification"""
    account_number: str = Field(..., min_length=10, max_length=10)
    pin: str = Field(..., min_length=4, max_length=4)


class TokenResponse(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    email: str
    full_name: str


class PINVerificationResponse(BaseModel):
    """Schema for PIN verification response"""
    verified: bool
    user_id: Optional[int] = None
    account_id: Optional[int] = None
    account_name: Optional[str] = None
    error: Optional[str] = None
