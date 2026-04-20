# app/routers/logs.py — versión protegida
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import HabitLog, Habit, User
from app.services.streak import get_stats
from app.services.auth import get_current_user

router = APIRouter(prefix="/habits/{habit_id}/logs", tags=["logs"])

MILESTONES = {7, 14, 30, 60, 100}


def _get_habit_or_403(habit_id: int, current_user: User, db: Session) -> Habit:
    """Helper: obtiene el hábito y verifica que pertenece al usuario."""
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    if habit.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return habit


@router.post("/")
def log_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = _get_habit_or_403(habit_id, current_user, db)

    existing = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.date == date.today()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya registrado hoy")

    db.add(HabitLog(habit_id=habit_id, date=date.today(), completed=True))
    db.commit()

    stats  = get_stats(habit_id, db)
    streak = stats["current_streak"]

    if streak in MILESTONES:
        from app.services.email import send_milestone
        send_milestone(current_user.email, current_user.name, habit.name, streak)

    return {"mensaje": "Registrado", **stats}


@router.get("/stats")
def habit_stats(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _get_habit_or_403(habit_id, current_user, db)
    return get_stats(habit_id, db)