from fastapi import FastAPI
from app.database import Base, engine
from app.routers import habits, logs, users
from app.scheduler import start_scheduler
import contextlib

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(title="Habit Tracker", lifespan=lifespan)
app.include_router(users.router)
app.include_router(habits.router)
app.include_router(logs.router)

Base.metadata.create_all(bind=engine)