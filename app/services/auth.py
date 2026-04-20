# app/services/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
import os
import hashlib
import bcrypt

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "cambia_esto_en_produccion")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")
EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

# Le dice a FastAPI dónde esperar el token (Header Authorization)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Contraseñas ──────────────────────────────────────────────────────────────

def _prehash(plain: str) -> bytes:
    """SHA256 primero → siempre 64 chars → nunca supera el límite de bcrypt."""
    return hashlib.sha256(plain.encode()).hexdigest().encode()

def hash_password(plain: str) -> str:
    hashed = bcrypt.hashpw(_prehash(plain), bcrypt.gensalt())
    return hashed.decode()   # Guardar como string en la DB

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_prehash(plain), hashed.encode())


# ── Tokens JWT ───────────────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """
    Genera el token JWT.
    'data' es lo que codificamos dentro (normalmente el email del usuario).
    """
    payload = data.copy()
    expire  = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
    payload.update({"exp": expire})          # Fecha de expiración
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> str:
    """
    Decodifica el token y devuelve el email.
    Lanza excepción si el token es inválido o expiró.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")      # "sub" = subject = email
        if email is None:
            raise ValueError("Token sin email")
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Usuario actual ───────────────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependencia que extrae el usuario del token.
    Se usa en cualquier endpoint que requiera autenticación.
    
    FastAPI llama esto automáticamente cuando ves:
        current_user: User = Depends(get_current_user)
    """
    email = decode_token(token)
    user  = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    return user