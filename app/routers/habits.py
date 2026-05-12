from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Habit, User
from app.services.auth import get_current_user
from app.schemas.habit import HabitCreate, HabitResponse, PaginatedHabitsResponse

router = APIRouter(prefix="/habits", tags=["habits"])

@router.post("/", response_model=HabitResponse)
def create_habit(
    habit_data: HabitCreate,                          # ← Body JSON ahora
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = Habit(
        user_id     = current_user.id,
        name        = habit_data.name,
        frequency   = habit_data.frequency,
        goal        = habit_data.goal,
        reminders   = habit_data.reminders or [],
        icon        = habit_data.icon,
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit

@router.get("/", response_model=PaginatedHabitsResponse)
def get_my_habits(
    page:  int = 1,      # Página actual (empieza en 1)
    limit: int = 5,      # Hábitos por página
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skip = (page - 1) * limit   # page=1 → skip=0, page=2 → skip=5

    total = db.query(Habit).filter(Habit.user_id == current_user.id).count()

    habits = (
        db.query(Habit)
        .filter(Habit.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "habits":      habits,
        "total":       total,
        "page":        page,
        "limit":       limit,
        "total_pages": -(-total // limit),  # Equivale a math.ceil(total / limit)
        "has_next":    page * limit < total,
        "has_prev":    page > 1,
    }


@router.delete("/{habit_id}")
def delete_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    if habit.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    db.delete(habit)
    db.commit()
    return {"mensaje": "Hábito eliminado"}

@router.get("/{habit_id}", response_model=HabitResponse)
def get_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    if habit.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return habit


@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    habit_data: HabitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    if habit.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    habit.name        = habit_data.name
    habit.frequency   = habit_data.frequency
    habit.goal        = habit_data.goal
    habit.reminders   = habit_data.reminders or []
    habit.icon        = habit_data.icon

    db.commit()
    db.refresh(habit)
    return habit