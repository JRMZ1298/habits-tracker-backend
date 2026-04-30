# app/services/badges.py
from sqlalchemy.orm import Session
from app.models import Badge, UserBadge, Habit
from app.services.streak import get_streak
from datetime import datetime

def check_and_award_badges(
    user_id: int,
    habit: Habit,
    db: Session
) -> list[Badge]:
    """
    Evalúa si el hábito cumple condiciones para desbloquear insignias.
    Devuelve la lista de insignias nuevas desbloqueadas.
    """
    current_streak = get_streak(habit.id, db)
    if current_streak == 0:
        return []

    # Insignias que aplican a este tipo de hábito (por icon/categoria)
    candidates = db.query(Badge).filter(
        Badge.category == habit.icon,
        Badge.required_streak <= current_streak
    ).all()

    newly_unlocked = []

    for badge in candidates:
        # Verificar que el usuario no la tenga ya
        already_has = db.query(UserBadge).filter(
            UserBadge.user_id == user_id,
            UserBadge.badge_id == badge.id
        ).first()

        if not already_has:
            user_badge = UserBadge(
                user_id     = user_id,
                badge_id    = badge.id,
                unlocked_at = datetime.utcnow()
            )
            db.add(user_badge)
            newly_unlocked.append(badge)

    if newly_unlocked:
        db.commit()

    return newly_unlocked