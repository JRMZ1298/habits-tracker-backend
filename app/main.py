import contextlib
from fastapi import FastAPI, Request
from app.database import engine, Base
from app.routers import auth, habits, logs, badges, stats, recomendations
from app.scheduler import start_scheduler
from fastapi.middleware.cors import CORSMiddleware
from app.seeds import seed_badges
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    seed_badges()           # ← Inserta badges si no existen
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(title="Habit Tracker", lifespan=lifespan)

# =========================
# 🚦 RATE LIMIT
# =========================
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )

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

app.include_router(auth.router)
app.include_router(habits.router)
app.include_router(logs.router)
app.include_router(stats.router)
app.include_router(badges.router)
app.include_router(recomendations.router)