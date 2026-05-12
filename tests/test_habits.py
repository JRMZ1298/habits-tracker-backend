def test_create_habit(client, auth_headers):
    response = client.post(
        "/habits/",
        json={
            "name": "Read books",
            "frequency": "daily",
            "goal": "Read 20 pages",
            "icon": "menu_book",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Read books"
    assert data["frequency"] == "daily"
    assert data["goal"] == "Read 20 pages"
    assert data["icon"] == "menu_book"
    assert "id" in data
    assert "created_at" in data


def test_list_habits(client, auth_headers):
    client.post(
        "/habits/",
        json={"name": "Habit 1", "frequency": "daily", "goal": "Goal 1", "icon": "favorite"},
        headers=auth_headers,
    )
    client.post(
        "/habits/",
        json={"name": "Habit 2", "frequency": "weekly", "goal": "Goal 2", "icon": "directions_run"},
        headers=auth_headers,
    )
    response = client.get("/habits/?page=1&limit=10", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["habits"]) == 2


def test_get_habit(client, auth_headers):
    create_resp = client.post(
        "/habits/",
        json={"name": "My Habit", "frequency": "daily", "goal": "My Goal", "icon": "water_drop"},
        headers=auth_headers,
    )
    habit_id = create_resp.json()["id"]

    response = client.get(f"/habits/{habit_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "My Habit"


def test_update_habit(client, auth_headers):
    create_resp = client.post(
        "/habits/",
        json={"name": "Old Name", "frequency": "daily", "goal": "Old Goal", "icon": "favorite"},
        headers=auth_headers,
    )
    habit_id = create_resp.json()["id"]

    response = client.put(
        f"/habits/{habit_id}",
        json={"name": "New Name", "frequency": "weekly", "goal": "New Goal", "icon": "menu_book"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["frequency"] == "weekly"


def test_delete_habit(client, auth_headers):
    create_resp = client.post(
        "/habits/",
        json={"name": "To Delete", "frequency": "daily", "goal": "Delete me", "icon": "favorite"},
        headers=auth_headers,
    )
    habit_id = create_resp.json()["id"]

    response = client.delete(f"/habits/{habit_id}", headers=auth_headers)
    assert response.status_code == 200

    get_resp = client.get(f"/habits/{habit_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_habit_requires_auth(client):
    response = client.post(
        "/habits/",
        json={"name": "No Auth", "frequency": "daily", "goal": "X", "icon": "favorite"},
    )
    assert response.status_code == 401


def test_habit_not_found(client, auth_headers):
    response = client.get("/habits/9999", headers=auth_headers)
    assert response.status_code == 404


def test_forbidden_habit_access(client, auth_headers):
    create_resp = client.post(
        "/habits/",
        json={"name": "Mine", "frequency": "daily", "goal": "X", "icon": "favorite"},
        headers=auth_headers,
    )
    habit_id = create_resp.json()["id"]

    other_user_resp = client.post(
        "/auth/register",
        json={"email": "other@test.com", "name": "Other", "password": "pass"}
    )
    other_token = client.post(
        "/auth/login",
        data={"username": "other@test.com", "password": "pass"}
    ).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    response = client.get(f"/habits/{habit_id}", headers=other_headers)
    assert response.status_code == 403
