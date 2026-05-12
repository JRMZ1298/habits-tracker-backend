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
