# app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.models import User, Habit, HabitLog
from app.services.email import send_reminder, send_weekly_summary
from datetime import date, timedelta
from app.services.streak import get_best_current_streak
from app.routers.stats import calculate_level
from sqlalchemy import func

def send_daily_reminders():
    """Envía recordatorio solo a usuarios con daily_reminder=True."""
    db = SessionLocal()
    try:
        # Solo usuarios con notificaciones activadas
        users = db.query(User).filter(User.daily_reminder == True).all()

        for user in users:
            # Hábitos pendientes hoy
            pending = []
            for habit in user.habits:
                logged_today = db.query(HabitLog).filter(
                    HabitLog.habit_id == habit.id,
                    HabitLog.date     == date.today()
                ).first()
                if not logged_today:
                    pending.append(habit.name)

            # Solo enviar si hay pendientes
            if pending:
                send_reminder(user.email, user.name, pending)
    finally:
        db.close()

def send_weekly_summaries():
    """Envía resumen semanal a usuarios con weekly_summary=True."""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.weekly_summary == True).all()
        today = date.today()
        week_start = today - timedelta(days=7)

        for user in users:
            # Completados esta semana
            total_week = (
                db.query(HabitLog)
                .join(Habit)
                .filter(
                    Habit.user_id      == user.id,
                    HabitLog.completed == True,
                    HabitLog.date      >= week_start,
                    HabitLog.date      <= today,
                )
                .count()
            )

            # Total histórico y nivel
            total_all_time = (
                db.query(HabitLog)
                .join(Habit)
                .filter(
                    Habit.user_id      == user.id,
                    HabitLog.completed == True,
                )
                .count()
            )
            level_data  = calculate_level(total_all_time)
            best_streak = get_best_current_streak(user.id, db)

            # Hábito con más completados esta semana
            top = (
                db.query(Habit.name, func.count(HabitLog.id).label("cnt"))
                .join(HabitLog)
                .filter(
                    Habit.user_id      == user.id,
                    HabitLog.completed == True,
                    HabitLog.date      >= week_start,
                )
                .group_by(Habit.id)
                .order_by(func.count(HabitLog.id).desc())
                .first()
            )

            # Datos por día de la semana
            days_data = []
            day_labels = ["Dom","Lun","Mar","Mié","Jue","Vie","Sáb"]
            for i in range(7):
                day = week_start + timedelta(days=i + 1)
                count = (
                    db.query(HabitLog)
                    .join(Habit)
                    .filter(
                        Habit.user_id      == user.id,
                        HabitLog.completed == True,
                        HabitLog.date      == day,
                    )
                    .count()
                )
                days_data.append({
                    "day":       day_labels[day.weekday()],
                    "completed": count
                })

            send_weekly_summary(
                to_email  = user.email,
                user_name = user.name,
                stats     = {
                    "total_week":    total_week,
                    "best_streak":   best_streak["streak"],
                    "level":         level_data["level"],
                    "total_all_time": total_all_time,
                    "top_habit":     top.name if top else None,
                    "days_data":     days_data,
                }
            )
    finally:
        db.close()


def start_scheduler():
    from sqlalchemy import func
    scheduler = BackgroundScheduler()

    # Recordatorio diario — 8:00 AM todos los días
    scheduler.add_job(
        send_daily_reminders,
        "cron",
        hour=8, minute=0,
        id="daily_reminder"
    )

    # Resumen semanal — lunes a las 9:00 AM
    scheduler.add_job(
        send_weekly_summaries,
        "cron",
        day_of_week="mon",
        hour=9, minute=0,
        id="weekly_summary"
    )

    scheduler.start()
    return scheduler