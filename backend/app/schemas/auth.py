from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: UUID
    email: str
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}
