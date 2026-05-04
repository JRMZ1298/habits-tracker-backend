from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import HabitLog, Habit
from app.services.auth import get_current_user
from app.models import User
from datetime import date, timedelta
from app.services.streak import (
    get_best_current_streak,
    get_best_historical_streak
)
from sqlalchemy import extract

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/weekly")
def get_weekly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    days_since_sunday = (today.weekday() + 1) % 7
    sunday = today - timedelta(days=days_since_sunday)

    result = []
    for i in range(7):
        day = sunday + timedelta(days=i)
        count = (
            db.query(HabitLog)
            .join(Habit)
            .filter(
                Habit.user_id  == current_user.id,
                HabitLog.date  == day,
                HabitLog.completed == True
            )
            .count()
        )
        result.append({
            "date":      day.isoformat(),
            "day":       day.strftime("%a"),
            "completed": count,
        })

    return result

@router.get("/today-count")
def get_today_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Total de hábitos completados hoy por el usuario."""
    count = (
        db.query(HabitLog)
        .join(Habit)
        .filter(
            Habit.user_id      == current_user.id,
            HabitLog.date      == date.today(),
            HabitLog.completed == True
        )
        .count()
    )
    return {"completed": count}

@router.get("/profile")
def get_user_profile_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Devuelve en una sola llamada:
    - Nivel del usuario
    - Progreso hacia el siguiente nivel
    - Mejor racha activa
    - Mejor racha histórica
    - Total de hábitos completados
    """
    # Total acumulado de todos los logs completados
    total_completed = (
        db.query(HabitLog)
        .join(Habit)
        .filter(
            Habit.user_id      == current_user.id,
            HabitLog.completed == True
        )
        .count()
    )

    HABITS_PER_LEVEL  = 10
    level             = (total_completed // HABITS_PER_LEVEL) + 1
    progress_in_level = total_completed % HABITS_PER_LEVEL   
    habits_to_next    = HABITS_PER_LEVEL - progress_in_level  

    best_current    = get_best_current_streak(current_user.id, db)
    best_historical = get_best_historical_streak(current_user.id, db)

    return {
        "level":              level,
        "total_completed":    total_completed,
        "progress_in_level":  progress_in_level, 
        "habits_to_next":     habits_to_next,      
        "habits_per_level":   HABITS_PER_LEVEL,
        "best_current_streak": {
            "streak": best_current["streak"],
            "habit":  best_current["habit"],   
        },
        "best_historical_streak": {
            "streak": best_historical["streak"],
            "habit":  best_historical["habit"],
        },
    }

@router.get("/yearly")
def get_yearly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Hábitos completados por mes del año actual (Enero-Diciembre).
    """
    current_year = date.today().year

    result = []
    for month in range(1, 13):
        count = (
            db.query(HabitLog)
            .join(Habit)
            .filter(
                Habit.user_id        == current_user.id,
                HabitLog.completed   == True,
                extract("year",  HabitLog.date) == current_year,
                extract("month", HabitLog.date) == month,
            )
            .count()
        )
        result.append({
            "month":     month,           # 1-12
            "label":     date(current_year, month, 1).strftime("%b"),  # "Jan", "Feb"...
            "completed": count,
        })

    return result