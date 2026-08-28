import pytest
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.config import settings
from app.database import Base, get_db, get_transaction
from app.main import app
from app.models import User, Ticket, Comment, TicketActivity, Category
from app.enums import TicketPriority, TicketStatus
from app.security import hash_password as get_password_hash

# 1. Setup the testing engine and SessionLocal specifically for tests
test_engine = create_engine(
    settings.TEST_DATABASE_URL
)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)

# Helper function to generate access tokens matching the fixture data structure
def create_access_token(data: dict) -> str:
    return jwt.encode(data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

# 2. Session-scoped database tables setup
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(
        bind=test_engine
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine
    )

# 3. Yield a database session bound to connection and transaction
@pytest.fixture
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(
        bind=connection
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

# 4. Yield TestClient overriding database dependencies (get_db and get_transaction)
@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    def override_get_transaction():
        yield db
        db.commit()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_transaction] = override_get_transaction

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

# 5. Model fixtures (no commits, only flushes)
@pytest.fixture
def customer(db):
    user = User(
        username="test_customer",
        email="customer@test.com",
        password_hash=get_password_hash(
            "Password123!"
        ),
        role="CUSTOMER",
        is_active=True
    )
    db.add(user)
    db.flush()
    return user

@pytest.fixture
def agent(db):
    user = User(
        username="test_agent",
        email="agent@test.com",
        password_hash=get_password_hash(
            "Password123!"
        ),
        role="AGENT",
        is_active=True
    )
    db.add(user)
    db.flush()
    return user

@pytest.fixture
def admin(db):
    user = User(
        username="test_admin",
        email="admin@test.com",
        password_hash=get_password_hash(
            "Password123!"
        ),
        role="ADMIN",
        is_active=True
    )
    db.add(user)
    db.flush()
    return user

@pytest.fixture
def category(db):
    cat = Category(
        name="IT Support"
    )
    db.add(cat)
    db.flush()
    return cat

@pytest.fixture
def ticket(db, customer, category):
    t = Ticket(
        title="Cannot log in to my account",
        description="I keep getting error",
        status=TicketStatus.OPEN,
        priority=TicketPriority.MEDIUM,
        category_id=category.id,
        created_by_id=customer.id
    )
    db.add(t)
    db.flush()
    return t

# 6. Token fixtures
@pytest.fixture
def customer_token(customer):
    return create_access_token(
        data={
            "sub": str(customer.id)
        }
    )

@pytest.fixture
def agent_token(agent):
    return create_access_token(
        data={
            "sub": str(agent.id)
        }
    )

@pytest.fixture
def admin_token(admin):
    return create_access_token(
        data={
            "sub": str(admin.id)
        }
    )
