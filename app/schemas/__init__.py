from app.schemas.auth import RegisterRequest, RegisterResponse, LoginResponse
from app.schemas.badge import BadgeResponse
from app.schemas.habit import HabitCreate, HabitResponse, PaginatedHabitsResponse
from app.schemas.log import LogResponse, StatsResponse, TodayLogResponse, NewBadgeInfo
from app.schemas.notification import NotificationPreferences, NotificationResponse
from app.schemas.stats import WeeklyDay, TodayCount, ProfileResponse, StreakInfo, YearlyMonth, PeriodProgress
from app.schemas.user import UpdateProfileRequest, ProfileUpdateResponse, TokenRefreshResponse

__all__ = [
    "RegisterRequest", "RegisterResponse", "LoginResponse",
    "BadgeResponse",
    "HabitCreate", "HabitResponse", "PaginatedHabitsResponse",
    "LogResponse", "StatsResponse", "TodayLogResponse", "NewBadgeInfo",
    "NotificationPreferences", "NotificationResponse",
    "WeeklyDay", "TodayCount", "ProfileResponse", "StreakInfo", "YearlyMonth", "PeriodProgress",
    "UpdateProfileRequest", "ProfileUpdateResponse", "TokenRefreshResponse",
]
