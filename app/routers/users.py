from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.services.auth import get_current_user, create_access_token
from app.schemas.user import UpdateProfileRequest, ProfileUpdateResponse, TokenRefreshResponse

router = APIRouter(prefix='/users', tags=['users'])

@router.put("/me", response_model=ProfileUpdateResponse)
def update_profile(
    data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar que el email nuevo no lo use otro usuario
    if data.email and data.email != current_user.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Este email ya está en uso"
            )
        current_user.email = data.email

    if data.name:
        current_user.name = data.name

    db.commit()
    db.refresh(current_user)

    return {
        "id":    current_user.id,
        "name":  current_user.name,
        "email": current_user.email,
    }

@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """Genera un nuevo token con los datos actuales del usuario."""
    token = create_access_token(data={"sub": current_user.email})
    return TokenRefreshResponse(access_token=token, token_type="bearer")