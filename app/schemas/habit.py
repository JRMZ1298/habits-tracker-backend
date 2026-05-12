from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class HabitCreate(BaseModel):
    name: str
    frequency: str
    goal: str
    reminders: Optional[List[str]] = []
    icon: str


class HabitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    frequency: str
    goal: str
    reminders: List[str]
    icon: str
    created_at: datetime


class PaginatedHabitsResponse(BaseModel):
    habits: List[HabitResponse]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool
