def test_get_notifications(client, auth_headers):
    response = client.get("/notifications/me/notifications", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "daily_reminder" in data
    assert "weekly_summary" in data


def test_update_notifications(client, auth_headers):
    response = client.put(
        "/notifications/me/notifications",
        json={"daily_reminder": False, "weekly_summary": True},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["daily_reminder"] is False
    assert data["weekly_summary"] is True


def test_get_notifications_requires_auth(client):
    response = client.get("/notifications/me/notifications")
    assert response.status_code == 401
