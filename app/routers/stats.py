from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import HabitLog, Habit
from app.services.auth import get_current_user
from app.models import User
from datetime import date, timedelta

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