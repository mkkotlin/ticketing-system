from app.models import User, Ticket
from app.security import hash_password, create_access_token
from app.enums import TicketPriority, TicketStatus

def test_create_comment(client, customer_token, ticket):
    response = client.post(
        f"/tickets/{ticket.id}/comments",
        headers={
            "Authorization": f"Bearer {customer_token}"
        },
        json={
            "content": "I am still facing this login issue."
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "I am still facing this login issue."
    assert "id" in data


def test_customer_cannot_comment_on_other_ticket(client, db, customer_token, category):
    # Create another customer and a ticket belonging to them
    another_customer = User(
        username="another_customer",
        email="another@test.com",
        password_hash=hash_password("Password123!"),
        role="CUSTOMER",
        is_active=True
    )
    db.add(another_customer)
    db.flush()

    other_ticket = Ticket(
        title="Other Customer Ticket",
        description="Private issues",
        status=TicketStatus.OPEN,
        priority=TicketPriority.MEDIUM,
        category_id=category.id,
        created_by_id=another_customer.id
    )
    db.add(other_ticket)
    db.flush()

    # The original customer tries to comment on the other customer's ticket
    response = client.post(
        f"/tickets/{other_ticket.id}/comments",
        headers={
            "Authorization": f"Bearer {customer_token}"
        },
        json={
            "content": "Malicious comment attempt"
        }
    )

    assert response.status_code == 403


def test_get_comments(client, customer_token, ticket):
    # Add a comment first
    client.post(
        f"/tickets/{ticket.id}/comments",
        headers={
            "Authorization": f"Bearer {customer_token}"
        },
        json={
            "content": "Initial comment"
        }
    )

    # Get comments
    response = client.get(
        f"/tickets/{ticket.id}/comments",
        headers={
            "Authorization": f"Bearer {customer_token}"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["content"] == "Initial comment"
