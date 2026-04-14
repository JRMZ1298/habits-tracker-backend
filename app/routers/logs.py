from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import HabitLog, Habit
from app.services.streak import get_stats
from app.services.email import send_streak_milestone

router = APIRouter(prefix="/habits/{habit_id}/logs", tags=["logs"])

MILESTONE_STREAKS = {7, 14, 30, 60, 100}

@router.post("/")
def log_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")

    # Evitar duplicados en el mismo día
    existing = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.date == date.today()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya registrado hoy")

    log = HabitLog(habit_id=habit_id, date=date.today(), completed=True)
    db.add(log)
    db.commit()

    stats = get_stats(habit_id, db)
    streak = stats["current_streak"]

    # Enviar correo si alcanza un hito
    if streak in MILESTONE_STREAKS:
        send_streak_milestone(
            habit.user.email,
            habit.user.name,
            habit.name,
            streak
        )

    return {"message": "Hábito registrado", **stats}


@router.get("/stats")
def habit_stats(habit_id: int, db: Session = Depends(get_db)):
    return get_stats(habit_id, db)