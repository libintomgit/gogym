import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET", "test-secret-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.dependencies import get_db
from app.main import app
from app.models.user import User
from app.services.auth import hash_password, create_access_token

# In-memory SQLite for tests — fast, isolated, disposable
SQLALCHEMY_TEST_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    """Provide a clean database session for each test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def client(db):
    """Test client with oerridden DB dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def create_test_user(db):
    """Factory fixture to create a test user."""
    def _create(email="user@test.com", password="testpass123", name="Test User", role="user"):
        user = User(
            email=email,
            hashed_password=hash_password(password),
            name=name,
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token({"sub": str(user.id)})
        return user, token
    return _create

@pytest.fixture
def test_user(create_test_user):
    """A default test user with token."""
    return create_test_user()

@pytest.fixture
def admin_user(create_test_user):
    """An admin user with token."""
    return create_test_user(
        email-"admin@test.com", name="Admin User", role="admin"
    )

@pytest.fixture
def auth_headers(test_user):
    """Authorization headers for the default test user."""
    _, token = test_user
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(admin_user):
    """Authorization headers for the admin user."""
    _, token = admin_user
    return {"Authorization": f"Bearer {token}"}


