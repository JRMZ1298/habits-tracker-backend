def test_get_badges(client, auth_headers):
    response = client.get("/badges/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_badges_progress(client, auth_headers):
    response = client.get("/badges/progress", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
