import contextlib
from fastapi import FastAPI, Request
from app.routers import auth, habits, logs, badges, stats, recommendations, notifications, users
from app.scheduler import start_scheduler
from fastapi.middleware.cors import CORSMiddleware
from app.seeds import seed_badges
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
from alembic.config import Config
from alembic import command

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    seed_badges()
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(title="Habit Tracker", lifespan=lifespan)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://TU-APP.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(habits.router)
app.include_router(logs.router)
app.include_router(stats.router)
app.include_router(badges.router)
app.include_router(recommendations.router)
app.include_router(notifications.router)
app.include_router(users.router)