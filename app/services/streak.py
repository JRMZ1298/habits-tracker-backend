from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, timedelta
from app.models import HabitLog, Habit

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

def get_best_current_streak(user_id: int, db: Session) -> dict:
    """Racha activa más alta entre todos los hábitos del usuario."""
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()

    best_streak  = 0
    best_habit   = None

    for habit in habits:
        streak = get_streak(habit.id, db)
        if streak > best_streak:
            best_streak = streak
            best_habit  = habit.name

    return {"streak": best_streak, "habit": best_habit}


def get_best_historical_streak(user_id: int, db: Session) -> dict:
    """Mejor racha que el usuario ha tenido en toda la historia."""
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()

    best_streak = 0
    best_habit  = None

    for habit in habits:
        logs = (
            db.query(HabitLog.date)
            .filter(HabitLog.habit_id == habit.id, HabitLog.completed == True)
            .order_by(HabitLog.date.asc())
            .all()
        )
        dates = sorted({log.date for log in logs})
        if not dates:
            continue

        # Calcular mejor racha histórica del hábito
        current_run = best_run = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days == 1:
                current_run += 1
                best_run = max(best_run, current_run)
            else:
                current_run = 1

        if best_run > best_streak:
            best_streak = best_run
            best_habit  = habit.name

    return {"streak": best_streak, "habit": best_habit}