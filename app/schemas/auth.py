from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_name: str
    user_email: str


class RegisterResponse(BaseModel):
    id: int
    email: str
    name: str


class LogoutResponse(BaseModel):
    mensaje: str
