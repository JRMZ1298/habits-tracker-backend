from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class NewBadgeInfo(BaseModel):
    name: str
    icon: str
    description: Optional[str]


class LogResponse(BaseModel):
    mensaje: str
    current_streak: int
    best_streak: int
    total: int
    new_badges: list[NewBadgeInfo]


class StatsResponse(BaseModel):
    current_streak: int
    best_streak: int
    total: int


class TodayLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    habit_id: int
    completed: bool
    date: date
