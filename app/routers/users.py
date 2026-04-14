from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

router = APIRouter(prefix='/users', tags=['users'])

@router.post('/') # POST /users/ — Crear usuario
def create_user(email: str, name: str, db: Session = Depends(get_db)):
# Verificar si el email ya existe
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail='Email ya registrado')
    user = User(email=email, name=name)
    db.add(user) # Preparar para guardar
    db.commit() # Guardar en la base de datos
    db.refresh(user)# Actualizar el objeto con el ID generado
    return user

@router.get('/') # GET /users/ — Listar usuarios
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()