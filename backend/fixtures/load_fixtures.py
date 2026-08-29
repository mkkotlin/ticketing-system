import os
import json
from sqlalchemy import text
from app.database import SessionLocal
from app.models import User, Category, Ticket, Comment, TicketActivity
from app.security import hash_password

def load_fixtures():
    db = SessionLocal()
    try:
        print("--- Clearing existing database data and resetting sequences ---")
        db.execute(text("TRUNCATE TABLE ticket_activities, comments, tickets, categories, \"user\" RESTART IDENTITY CASCADE;"))
        db.commit()

        # Determine the paths of the fixture files
        current_dir = os.path.dirname(os.path.abspath(__file__))
        users_file = os.path.join(current_dir, "users.json")
        categories_file = os.path.join(current_dir, "categories.json")
        tickets_file = os.path.join(current_dir, "tickets.json")

        print("\n--- Loading Users ---")
        with open(users_file, "r") as f:
            users_data = json.load(f)
        
        user_id_map = {}
        for u_data in users_data:
            # Check if user exists
            existing_user = db.query(User).filter(User.username == u_data["username"]).first()
            if not existing_user:
                print(f"Creating user: {u_data['username']}")
                hashed = hash_password(u_data["password"])
                user = User(
                    username=u_data["username"],
                    email=u_data["email"],
                    password_hash=hashed,
                    role=u_data["role"]
                )
                db.add(user)
                db.flush() # Flush to get the ID
                user_id_map[u_data["username"]] = user.id
            else:
                print(f"User already exists: {u_data['username']}")
                user_id_map[u_data["username"]] = existing_user.id

        print("\n--- Loading Categories ---")
        with open(categories_file, "r") as f:
            categories_data = json.load(f)
        
        for cat_data in categories_data:
            # Check if category exists
            existing_cat = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not existing_cat:
                print(f"Creating category: {cat_data['name']}")
                category = Category(
                    name=cat_data["name"]
                )
                db.add(category)
            else:
                print(f"Category already exists: {cat_data['name']}")

        db.flush()

        print("\n--- Loading Tickets ---")
        with open(tickets_file, "r") as f:
            tickets_data = json.load(f)
        
        for t_data in tickets_data:
            # Get created_by_id from username
            username = t_data["created_by_username"]
            created_by_id = user_id_map.get(username)
            category_id = t_data["category_id"]

            # Check if ticket already exists (by title)
            existing_ticket = db.query(Ticket).filter(Ticket.title == t_data["title"]).first()
            if not existing_ticket:
                print(f"Creating ticket: {t_data['title']}")
                ticket = Ticket(
                    title=t_data["title"],
                    description=t_data["description"],
                    status=t_data["status"],
                    priority=t_data["priority"],
                    category_id=category_id,
                    created_by_id=created_by_id
                )
                db.add(ticket)
            else:
                print(f"Ticket already exists: {t_data['title']}")

        db.commit()
        print("\nAll fixtures loaded successfully!")
    except Exception as e:
        db.rollback()
        print(f"\nError occurred: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    load_fixtures()
