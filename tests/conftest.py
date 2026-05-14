import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models import User
from app.routers import auth, habits, logs, badges, stats, notifications, users
from app.services.auth import hash_password, create_access_token


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    test_app = FastAPI(title="Test App")
    test_app.include_router(auth.router)
    test_app.include_router(habits.router)
    test_app.include_router(logs.router)
    test_app.include_router(stats.router)
    test_app.include_router(badges.router)
    test_app.include_router(notifications.router)
    test_app.include_router(users.router)

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as c:
        yield c


@pytest.fixture(scope="function")
def auth_headers(db_session, client):
    user = User(
        email="test@test.com",
        name="Test",
        hashed_password=hash_password("secret123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(data={"sub": user.email})
    return {"Authorization": f"Bearer {token}"}
