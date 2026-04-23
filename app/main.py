import contextlib
from fastapi import FastAPI
from app.database import engine, Base
from app import models
from app.routers import auth, habits, logs
from app.scheduler import start_scheduler
from fastapi.middleware.cors import CORSMiddleware

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(title="Habit Tracker", lifespan=lifespan)

# ── CORS — agregar esto antes de los routers ──────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL de tu React en desarrollo
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],    # GET, POST, DELETE, PUT, etc.
    allow_headers=["*"],    # Authorization, Content-Type, etc.
)
# ─────────────────────────────────────────────────────────────────────────────

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)      # ← NUEVO (va primero)
app.include_router(habits.router)
app.include_router(logs.router)