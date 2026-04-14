# app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.models import User, Habit, HabitLog
from app.services.email import send_reminder
from datetime import date

def send_daily_reminders():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            # Hábitos que aún no tienen log hoy
            pending = []
            for habit in user.habits:
                logged_today = db.query(HabitLog).filter(
                    HabitLog.habit_id == habit.id,
                    HabitLog.date == date.today()
                ).first()
                if not logged_today:
                    pending.append(habit.name)

            if pending:
                send_reminder(user.email, user.name, pending)
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Todos los días a las 8:00 AM
    scheduler.add_job(send_daily_reminders, "cron", hour=8, minute=0)
    scheduler.start()
    return scheduler