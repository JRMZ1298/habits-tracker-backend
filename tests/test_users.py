def test_update_profile(client, auth_headers):
    response = client.put(
        "/users/me",
        json={"name": "New Name", "email": "newemail@test.com"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["email"] == "newemail@test.com"


def test_update_profile_name_only(client, auth_headers):
    response = client.put(
        "/users/me",
        json={"name": "Only Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Only Name"


def test_refresh_token(client, auth_headers):
    response = client.post("/users/refresh", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_update_profile_requires_auth(client):
    response = client.put(
        "/users/me",
        json={"name": "Hacker"},
    )
    assert response.status_code == 401
