from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Badge, UserBadge, Habit, User
from app.services.auth import get_current_user
from app.services.streak import get_streak
from app.schemas.badge import BadgeResponse

router = APIRouter(prefix="/badges", tags=["badges"])


@router.get("/", response_model=list[BadgeResponse])
def get_my_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Devuelve TODAS las insignias con unlocked=True/False según el usuario."""
    all_badges = db.query(Badge).all()

    # IDs que el usuario ya desbloqueó
    unlocked = db.query(UserBadge).filter(
        UserBadge.user_id == current_user.id
    ).all()
    unlocked_map = {ub.badge_id: ub.unlocked_at for ub in unlocked}

    result = []
    for badge in all_badges:
        result.append({
            **badge.__dict__,
            "unlocked":    badge.id in unlocked_map,
            "unlocked_at": unlocked_map.get(badge.id),
        })

    return result

@router.get("/progress")
def get_badges_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Para cada categoría, devuelve la racha más alta que tiene el usuario."""
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()

    # Racha máxima por categoría (icon del hábito)
    progress: dict[str, int] = {}
    for habit in habits:
        if not habit.icon:
            continue
        streak = get_streak(habit.id, db)
        current = progress.get(habit.icon, 0)
        progress[habit.icon] = max(current, streak)

    return progress  # { "water_drop": 23, "directions_run": 8 }