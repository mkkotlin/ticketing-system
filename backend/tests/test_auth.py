def test_root(client):
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Ticketing System API"
    }


def test_login(client, customer):
    response = client.post(
        "/auth/login",
        data={
            "username": customer.username,
            "password": "Password123!"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_tickets_requires_authentication(client):
    response = client.get("/tickets")

    assert response.status_code == 401
