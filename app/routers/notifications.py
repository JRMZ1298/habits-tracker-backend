from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.services.auth import get_current_user
from app.schemas.notification import NotificationPreferences, NotificationResponse

router = APIRouter(prefix='/notifications', tags=['notifications'])

@router.put("/me/notifications", response_model=NotificationResponse)
def update_notifications(
    prefs: NotificationPreferences,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.daily_reminder = prefs.daily_reminder
    current_user.weekly_summary = prefs.weekly_summary
    db.commit()
    db.refresh(current_user)
    return {
        "daily_reminder": current_user.daily_reminder,
        "weekly_summary": current_user.weekly_summary,
    }

@router.get("/me/notifications", response_model=NotificationResponse)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "daily_reminder": current_user.daily_reminder,
        "weekly_summary": current_user.weekly_summary,
    }