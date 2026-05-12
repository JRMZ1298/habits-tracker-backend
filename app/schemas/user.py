from pydantic import BaseModel, EmailStr
from typing import Optional


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class ProfileUpdateResponse(BaseModel):
    id: int
    name: Optional[str]
    email: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str
