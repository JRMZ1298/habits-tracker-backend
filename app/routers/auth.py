from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.services.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(email: str, name: str, password: str,
             db: Session = Depends(get_db)):
    """Registrar un nuevo usuario con contraseña hasheada."""
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")

    user = User(
        email=email,
        name=name,
        hashed_password=hash_password(password)   # Nunca guardamos la original
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "name": user.name}


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    """
    Login estándar OAuth2.
    Recibe 'username' (aquí es el email) y 'password'.
    Devuelve el token JWT.
    """
    user = db.query(User).filter(User.email == form.username).first()

    # Verificar usuario Y contraseña en el mismo mensaje
    # (no revelar si el email existe o no — seguridad básica)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    token = create_access_token(data={"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",        # Estándar OAuth2
        "user_name": user.name
    }