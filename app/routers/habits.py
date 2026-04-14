from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Habit, User

router = APIRouter(prefix='/habits', tags=['habits'])

@router.post('/') # POST /habits/ — Crear hábito
def create_habit(user_id: int, name: str, description: str = '',
db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    habit = Habit(user_id=user_id, name=name, description=description)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit

@router.get('/user/{user_id}') # GET — Hábitos de un usuario
def get_habits(user_id: int, db: Session = Depends(get_db)):
    return db.query(Habit).filter(Habit.user_id == user_id).all()