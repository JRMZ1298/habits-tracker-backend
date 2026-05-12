from pydantic import BaseModel


class NotificationPreferences(BaseModel):
    daily_reminder: bool
    weekly_summary: bool


class NotificationResponse(BaseModel):
    daily_reminder: bool
    weekly_summary: bool
