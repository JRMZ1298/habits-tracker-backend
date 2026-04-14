from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, timedelta
from app.models import HabitLog

def get_streak(habit_id: int, db: Session) -> int:
    """
    Cuenta cuántos días consecutivos tiene el hábito
    hasta hoy o ayer (si hoy aún no se ha registrado).
    """
    logs = (
        db.query(HabitLog.date)
        .filter(HabitLog.habit_id == habit_id, HabitLog.completed == True)
        .order_by(HabitLog.date.desc())
        .all()
    )

    if not logs:
        return 0

    dates = {log.date for log in logs}
    today = date.today()
    streak = 0

    # Empezamos desde hoy; si hoy no está, probamos desde ayer
    current = today if today in dates else today - timedelta(days=1)

    while current in dates:
        streak += 1
        current -= timedelta(days=1)

    return streak


def get_stats(habit_id: int, db: Session) -> dict:
    """Estadísticas: racha actual, mejor racha, total completados."""
    logs = (
        db.query(HabitLog.date)
        .filter(HabitLog.habit_id == habit_id, HabitLog.completed == True)
        .order_by(HabitLog.date.asc())
        .all()
    )
    dates = sorted({log.date for log in logs})
    
    if not dates:
        return {"current_streak": 0, "best_streak": 0, "total": 0}

    # Calcular mejor racha histórica
    best = current_run = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            current_run += 1
            best = max(best, current_run)
        else:
            current_run = 1

    return {
        "current_streak": get_streak(habit_id, db),
        "best_streak": best,
        "total": len(dates),
    }