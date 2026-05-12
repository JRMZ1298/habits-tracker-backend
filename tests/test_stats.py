def test_weekly_stats(client, auth_headers):
    response = client.get("/stats/weekly", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    for day in data:
        assert "date" in day
        assert "day" in day
        assert "completed" in day


def test_today_count(client, auth_headers):
    response = client.get("/stats/today-count", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "completed" in data


def test_profile(client, auth_headers):
    response = client.get("/stats/profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "level" in data
    assert "total_completed" in data
    assert "best_current_streak" in data
    assert "best_historical_streak" in data


def test_yearly_stats(client, auth_headers):
    response = client.get("/stats/yearly", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 12
    for month in data:
        assert "month" in month
        assert "label" in month
        assert "completed" in month
