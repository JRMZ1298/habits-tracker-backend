
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

# Lee la URL de la base de datos del archivo .env
# Si no existe, usa SQLite (un archivo local, ideal para empezar)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./habits.db")

# 'engine' es la conexión real a la base de datos
engine = create_engine(DATABASE_URL)
# 'SessionLocal' es la fábrica de sesiones (conexiones temporales)
SessionLocal = sessionmaker(bind=engine)

# Clase base que usarán todos los modelos
class Base(DeclarativeBase):
    pass

# Esta función abre y cierra la conexión automáticamente
def get_db():
    db = SessionLocal()
    try:
        yield db  # 'yield' pausa aquí mientras FastAPI usa 'db'
    finally:
        db.close()  # Siempre cierra la conexión al terminar