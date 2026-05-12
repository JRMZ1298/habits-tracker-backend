from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class BadgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    name: str
    icon: str
    description: Optional[str]
    category: str
    required_streak: int
    unlocked: bool
    unlocked_at: Optional[datetime]
