# app/routers/habits.py — versión protegida
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Habit, User
from app.services.auth import get_current_user   # ← NUEVO

router = APIRouter(prefix="/habits", tags=["habits"])


@router.post("/")
def create_habit(
    name: str,
    description: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)   # ← NUEVO
):
    """
    current_user viene del token JWT automáticamente.
    Ya no necesitamos que el usuario mande su user_id — lo sabemos del token.
    """
    habit = Habit(
        user_id=current_user.id,    # ID del token, no del body
        name=name,
        description=description
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.get("/")
def get_my_habits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Solo devuelve los hábitos del usuario autenticado."""
    return db.query(Habit).filter(Habit.user_id == current_user.id).all()


@router.delete("/{habit_id}")
def delete_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()

    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")

    # Verificar que el hábito pertenece al usuario del token
    if habit.user_id != current_user.id:
        raise HTTPException(
            status_code=403,           # 403 = Forbidden (distinto de 401)
            detail="No tienes permiso para eliminar este hábito"
        )

    db.delete(habit)
    db.commit()
    return {"mensaje": "Hábito eliminado"}