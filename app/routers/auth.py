from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.services.auth import hash_password, verify_password, create_access_token, revoke_token, get_current_user, oauth2_scheme
from app.core.config import settings
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginResponse, LogoutResponse
from app.core.limiter import limiter
import httpx
from urllib.parse import urlencode

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse)
@limiter.limit("5/minute")
def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")

    user = User(
        email=body.email,
        name=body.name,
        hashed_password=hash_password(body.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return RegisterResponse(id=user.id, email=user.email, name=user.name)


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    """
    Login estándar OAuth2.
    Recibe 'username' (aquí es el email) y 'password'.
    Devuelve el token JWT.
    """
    user = db.query(User).filter(User.email == form.username).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # 🔥 usuario OAuth sin password
    if not user.hashed_password:
        raise HTTPException(
        status_code=400,
        detail="This account uses Google Sign-In"
    )

    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.email})
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user_name=user.name,
        user_email=user.email
    )

@router.post("/logout", response_model=LogoutResponse)
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    revoke_token(token, db)
    return LogoutResponse(mensaje="Sesión cerrada")


GOOGLE_CLIENT_ID     = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI  = settings.GOOGLE_REDIRECT_URI
FRONTEND_URL         = settings.FRONTEND_URL

GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_URL  = "https://www.googleapis.com/oauth2/v2/userinfo"


@router.get("/google")
def google_login():
    """
    Redirige al usuario a la pantalla de login de Google.
    """
    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "online",
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Google redirige aquí con un 'code'.
    Lo intercambiamos por el perfil del usuario.
    """
    # 1. Intercambiar code por access_token de Google
    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_URL, data={
            "code":          code,
            "client_id":     GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri":  GOOGLE_REDIRECT_URI,
            "grant_type":    "authorization_code",
        })

    token_data = token_response.json()

    if "error" in token_data:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(f"{FRONTEND_URL}/login?error=google_failed")

    # 2. Obtener datos del usuario de Google
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            GOOGLE_USER_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )

    google_user = user_response.json()
    email       = google_user.get("email")
    name        = google_user.get("name", email)

    if not email:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(f"{FRONTEND_URL}/login?error=no_email")

    # 3. Buscar o crear el usuario
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # Usuario nuevo — crear sin contraseña (no puede hacer login con email/pass)
        user = User(
            email           = email,
            name            = name,
            hashed_password = "",   # vacío — solo puede loguearse con Google
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 4. Generar nuestro JWT y redirigir al frontend
    token = create_access_token(data={"sub": user.email})

    from fastapi.responses import RedirectResponse
    return RedirectResponse(
        f"{FRONTEND_URL}/auth/callback?token={token}&name={user.name}"
    )