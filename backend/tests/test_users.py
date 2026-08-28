def test_customer_cannot_get_users(client, customer_token):
    response = client.get(
        "/users",
        headers={
            "Authorization": f"Bearer {customer_token}"
        }
    )
    assert response.status_code == 403


def test_agent_cannot_get_users(client, agent_token):
    response = client.get(
        "/users",
        headers={
            "Authorization": f"Bearer {agent_token}"
        }
    )
    assert response.status_code == 403


def test_admin_can_get_users(client, admin_token):
    response = client.get(
        "/users",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )
    assert response.status_code == 200


def test_get_user_by_id(client, admin_token, customer):
    response = client.get(
        f"/users/{customer.id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == customer.username
    assert data["email"] == customer.email


def test_update_user_role(client, admin_token, customer):
    response = client.patch(
        f"/users/{customer.id}/role",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "role": "AGENT"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "AGENT"


def test_admin_cannot_change_own_role(client, admin, admin_token):
    response = client.patch(
        f"/users/{admin.id}/role",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "role": "AGENT"
        }
    )
    assert response.status_code == 400


def test_delete_user(client, admin_token, customer):
    response = client.delete(
        f"/users/{customer.id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )
    assert response.status_code == 204


def test_admin_cannot_delete_self(client, admin, admin_token):
    response = client.delete(
        f"/users/{admin.id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )
    assert response.status_code == 400


def test_update_user_status(client, admin_token, customer):
    response = client.patch(
        f"/users/{customer.id}/status",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "is_active": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


def test_admin_cannot_change_own_status(client, admin, admin_token):
    response = client.patch(
        f"/users/{admin.id}/status",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "is_active": False
        }
    )
    assert response.status_code == 400
