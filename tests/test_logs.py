import pytest


@pytest.fixture
def habit_id(client, auth_headers):
    resp = client.post(
        "/habits/",
        json={"name": "Test Habit", "frequency": "daily", "goal": "Test", "icon": "favorite"},
        headers=auth_headers,
    )
    return resp.json()["id"]


def test_log_habit(client, auth_headers, habit_id):
    response = client.post(f"/habits/{habit_id}/logs", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["mensaje"] == "Registrado"


def test_log_habit_twice(client, auth_headers, habit_id):
    client.post(f"/habits/{habit_id}/logs", headers=auth_headers)
    response = client.post(f"/habits/{habit_id}/logs", headers=auth_headers)
    assert response.status_code == 400
    assert "Ya registrado" in response.json()["detail"]


def test_get_stats(client, auth_headers, habit_id):
    response = client.get(f"/habits/{habit_id}/logs/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "current_streak" in data
    assert "best_streak" in data
    assert "total" in data


def test_get_today_log(client, auth_headers, habit_id):
    response = client.get(f"/habits/{habit_id}/logs/today", headers=auth_headers)
    assert response.status_code == 200


def test_log_requires_auth(client, habit_id):
    response = client.post(f"/habits/{habit_id}/logs")
    assert response.status_code == 401
