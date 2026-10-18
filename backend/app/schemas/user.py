from typing import Optional
from pydantic import BaseModel, Field
from app.models.user import UserRole

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class UserBase(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX, description="RFC 5322 compliant clinical email address")
    full_name: str = Field(..., min_length=2, max_length=255)
    role: UserRole = UserRole.PATIENT
    license_credential_id: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX)
    password: str


class UserResponse(UserBase):
    id: str
    is_active: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    sub: str
    role: UserRole
    license_credential_id: Optional[str] = None
