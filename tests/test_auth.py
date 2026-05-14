def test_register(client):
    response = client.post(
        "/auth/register",
        json={"email": "new@test.com", "name": "New", "password": "pass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@test.com"
    assert data["name"] == "New"
    assert "id" in data


def test_register_duplicate_email(client):
    client.post(
        "/auth/register",
        json={"email": "dup@test.com", "name": "First", "password": "pass123"}
    )
    response = client.post(
        "/auth/register",
        json={"email": "dup@test.com", "name": "Second", "password": "pass456"}
    )
    assert response.status_code == 400
    assert "ya registrado" in response.json()["detail"].lower()


def test_login(client):
    client.post(
        "/auth/register",
        json={"email": "login@test.com", "name": "Login", "password": "pass123"}
    )
    response = client.post(
        "/auth/login",
        data={"username": "login@test.com", "password": "pass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_email"] == "login@test.com"


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        data={"username": "noone@test.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_register_missing_fields(client):
    response = client.post(
        "/auth/register",
        json={"email": "bad@test.com"}
    )
    assert response.status_code == 422


def test_logout_success(db_session, client):
    from app.models import User
    from app.services.auth import hash_password, create_access_token

    user = User(
        email="logout@test.com",
        name="Logout",
        hashed_password=hash_password("pass123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(data={"sub": user.email})
    response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "mensaje" in data


def test_logout_token_revoked(db_session, client):
    from app.models import User
    from app.services.auth import hash_password, create_access_token

    user = User(
        email="revoke@test.com",
        name="Revoke",
        hashed_password=hash_password("pass123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(data={"sub": user.email})
    client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert "revocado" in response.json()["detail"].lower()


def test_logout_without_token(client):
    response = client.post("/auth/logout")
    assert response.status_code == 401
