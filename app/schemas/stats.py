from pydantic import BaseModel
from typing import Optional


class WeeklyDay(BaseModel):
    date: str
    day: str
    completed: int


class TodayCount(BaseModel):
    completed: int


class StreakInfo(BaseModel):
    streak: int
    habit: Optional[str]


class ProfileResponse(BaseModel):
    level: int
    progress_in_level: int
    habits_per_level: int
    habits_to_next: int
    total_completed: int
    best_current_streak: StreakInfo
    best_historical_streak: StreakInfo


class YearlyMonth(BaseModel):
    month: int
    label: str
    completed: int


class PeriodProgress(BaseModel):
    habit_id: int
    frequency: str
    period_start: str
    period_end: str
    completed: int
    total_bars: int
    completed_bars: int
    percentage: int
    progress: str
