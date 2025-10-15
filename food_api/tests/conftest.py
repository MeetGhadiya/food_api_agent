"""
Pytest Configuration and Fixtures
Shared test fixtures for the FoodieExpress test suite
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.models import User, Restaurant, Order, Review
from app.security import hash_password


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Initialize database before running tests"""
    await init_db()
    yield
    # Cleanup after tests if needed


@pytest.fixture
def client():
    """Create a synchronous HTTP client for testing FastAPI endpoints"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create an async HTTP client for testing FastAPI endpoints"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_user():
    """Create a test user for authentication tests"""
    # Clean up any existing test user
    existing_user = await User.find_one(User.username == "testuser")
    if existing_user:
        await existing_user.delete()
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        role="user"
    )
    await user.insert()
    yield user
    
    # Cleanup
    await user.delete()


@pytest.fixture
async def test_admin():
    """Create a test admin user"""
    existing_admin = await User.find_one(User.username == "testadmin")
    if existing_admin:
        await existing_admin.delete()
    
    admin = User(
        username="testadmin",
        email="admin@example.com",
        hashed_password=hash_password("adminpass123"),
        role="admin"
    )
    await admin.insert()
    yield admin
    
    # Cleanup
    await admin.delete()


@pytest.fixture
def auth_token(client, test_user):
    """Get an authentication token for a test user"""
    response = client.post(
        "/users/login",
        data={
            "username": test_user.username,
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def sample_restaurant():
    """Create a test restaurant (alias for test_restaurant)"""
    return test_restaurant()


@pytest.fixture
async def test_restaurant():
    """Create a test restaurant"""
    existing = await Restaurant.find_one(Restaurant.name == "Test Restaurant")
    if existing:
        await existing.delete()
    
    restaurant = Restaurant(
        name="Test Restaurant",
        area="Test Area",
        cuisine="Test Cuisine",
        items=[
            {"item_name": "Test Item 1", "price": 100},
            {"item_name": "Test Item 2", "price": 150}
        ]
    )
    await restaurant.insert()
    yield restaurant
    
    # Cleanup
    await restaurant.delete()


# Test data constants
TEST_VALID_EMAIL = "valid@example.com"
TEST_VALID_PASSWORD = "SecurePass123!"
TEST_INVALID_EMAIL = "not-an-email"
TEST_WEAK_PASSWORD = "123"
