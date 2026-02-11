import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session
from sqlmodel.pool import StaticPool
from datetime import datetime, timedelta
from jose import jwt

from src.main import app
from src.models.user_model import User
from src.config.settings import settings
from src.utils.jwt import create_access_token, JWTData


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    """Create an in-memory database session for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
    from src.database import SQLModel
    SQLModel.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session


def test_register_user_success(client, db_session):
    """Test successful user registration"""
    # Arrange
    user_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "name": "Test User"
    }

    # Act
    response = client.post("/api/v1/auth/register", json=user_data)

    # Assert
    assert response.status_code == 200

    # Check that response contains token and user info
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == user_data["email"]
    assert data["user"]["name"] == user_data["name"]

    # Verify that token is valid
    token = data["token"]
    decoded = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert decoded["email"] == user_data["email"]


def test_register_user_duplicate_email(client, db_session):
    """Test registration with duplicate email fails"""
    # Arrange - register user first
    user_data = {
        "email": "duplicate@example.com",
        "password": "securepassword123",
        "name": "Test User"
    }

    # Register the user first
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200

    # Act - try to register with same email
    response = client.post("/api/v1/auth/register", json=user_data)

    # Assert
    assert response.status_code == 409  # Conflict
    data = response.json()
    assert "already exists" in data["detail"]


def test_login_user_success(client, db_session):
    """Test successful user login"""
    # Arrange - register a user first
    user_data = {
        "email": "login@example.com",
        "password": "securepassword123",
        "name": "Login User"
    }

    # Register the user
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 200

    # Act - login with correct credentials
    login_data = {
        "email": "login@example.com",
        "password": "securepassword123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)

    # Assert
    assert response.status_code == 200

    # Check that response contains token and user info
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == login_data["email"]


def test_login_user_invalid_credentials(client, db_session):
    """Test login with invalid credentials fails"""
    # Arrange - register a user first
    user_data = {
        "email": "invalid@example.com",
        "password": "securepassword123",
        "name": "Invalid User"
    }

    # Register the user
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 200

    # Act - try to login with wrong password
    login_data = {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", json=login_data)

    # Assert
    assert response.status_code == 401  # Unauthorized
    data = response.json()
    assert "password" in data["detail"]


def test_logout_user(client, db_session):
    """Test user logout"""
    # Arrange - register and login a user
    user_data = {
        "email": "logout@example.com",
        "password": "securepassword123",
        "name": "Logout User"
    }

    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 200

    login_data = {
        "email": "logout@example.com",
        "password": "securepassword123"
    }
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200

    # Act
    response = client.post("/api/v1/auth/logout")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"


def test_protected_route_without_auth(client):
    """Test that protected routes return 401 without authentication"""
    # Act - try to access protected route without auth
    response = client.get("/api/v1/users/nonexistent/tasks")

    # Assert
    assert response.status_code == 401


def test_protected_route_with_valid_auth(client, db_session):
    """Test that protected routes work with valid authentication"""
    # Arrange - register and get token
    user_data = {
        "email": "protected@example.com",
        "password": "securepassword123",
        "name": "Protected User"
    }

    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 200

    token = register_response.json()["token"]

    # Act - try to access protected route with valid auth
    response = client.get(
        "/api/v1/tasks/protected@example.com",
        headers={"Authorization": f"Bearer {token}"}
    )

    # For this test, we expect a 403 because the user_id in URL doesn't match JWT user_id
    # The system checks that URL user_id matches JWT user_id
    assert response.status_code == 403