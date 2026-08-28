from app.models import User, Ticket
from app.security import hash_password, create_access_token
from app.enums import TicketPriority, TicketStatus

def test_customer_can_get_tickets(client, customer_token):
    response = client.get(
        "/tickets",
        headers={
            "Authorization": f"Bearer {customer_token}"
        }
    )
    assert response.status_code == 200


def test_customer_can_create_ticket(client, customer_token, category):
    response = client.post(
        "/tickets",
        headers={
            "Authorization": f"Bearer {customer_token}"
        },
        json={
            "title": "VPN is not working",
            "description": "Unable to connect to VPN",
            "priority": "HIGH",
            "category_id": category.id
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "VPN is not working"
    assert data["priority"] == "HIGH"
    assert data["status"] == "OPEN"


def test_customer_cannot_assign_ticket(client, customer_token, ticket, agent):
    response = client.post(
        f"/tickets/{ticket.id}/assign",
        headers={
            "Authorization": f"Bearer {customer_token}"
        },
        json={
            "agent_id": agent.id
        }
    )
    assert response.status_code == 403


def test_admin_can_assign_ticket(client, admin_token, ticket, agent):
    response = client.post(
        f"/tickets/{ticket.id}/assign",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "agent_id": agent.id
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["assigned_to_id"] == agent.id


def test_agent_can_update_assigned_ticket(client, agent_token, ticket, agent, db):
    # Assign the ticket to the agent first
    ticket.assigned_to_id = agent.id
    db.flush()

    response = client.patch(
        f"/tickets/{ticket.id}",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
        json={
            "status": "IN_PROGRESS"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "IN_PROGRESS"


def test_agent_cannot_update_unassigned_ticket(client, agent_token, ticket):
    response = client.patch(
        f"/tickets/{ticket.id}",
        headers={
            "Authorization": f"Bearer {agent_token}"
        },
        json={
            "status": "IN_PROGRESS"
        }
    )
    assert response.status_code == 403


def test_customer_cannot_access_other_customer_ticket(client, db, ticket):
    # Create another customer
    another_customer = User(
        username="another_customer",
        email="another@test.com",
        password_hash=hash_password("Password123!"),
        role="CUSTOMER",
        is_active=True
    )
    db.add(another_customer)
    db.flush()

    token = create_access_token(user_id=another_customer.id)

    response = client.get(
        f"/tickets/{ticket.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 403


def test_invalid_ticket_status_transition(client, admin_token, ticket):
    response = client.patch(
        f"/tickets/{ticket.id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "status": "CLOSED"
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "INVALID_STATUS_TRANSITION"


def test_ticket_activity(client, admin_token, ticket, agent):
    response = client.post(
        f"/tickets/{ticket.id}/assign",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "agent_id": agent.id
        }
    )
    assert response.status_code == 200

    response = client.get(
        f"/tickets/{ticket.id}/activities",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200
    activities = response.json()
    assert any(
        activity["action"] == "ASSIGNED"
        for activity in activities
    )


def test_inactive_user_cannot_access_api(client, customer, customer_token, db):
    customer.is_active = False
    db.flush()

    response = client.get(
        "/tickets",
        headers={
            "Authorization": f"Bearer {customer_token}"
        }
    )

    assert response.status_code == 403
    data = response.json()
    assert data["error"] == "ACCOUNT_INACTIVE"
    assert data["message"] == "User account is inactive"
