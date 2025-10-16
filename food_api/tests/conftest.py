"""
Pytest Configuration and Fixtures
Shared test fixtures for the FoodieExpress test suite
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.models import User, Restaurant, Order, Review, OrderItem
from app.security import hash_password


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# Remove the session-scoped setup_database fixture
# Database will be initialized automatically by Beanie


@pytest.fixture
def client():
    """Create a synchronous HTTP client for testing FastAPI endpoints"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create an async HTTP client for testing FastAPI endpoints"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
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
    try:
        await user.delete()
    except:
        pass  # Already deleted


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
    try:
        await admin.delete()
    except:
        pass  # Already deleted


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
async def auth_token_async(async_client, test_user):
    """Get an authentication token for a test user (async version)"""
    response = await async_client.post(
        "/users/login",
        data={
            "username": test_user.username,
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def admin_auth_token_async(async_client, test_admin):
    """Get an authentication token for admin user (async version)"""
    response = await async_client.post(
        "/users/login",
        data={
            "username": test_admin.username,
            "password": "adminpass123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def multiple_test_restaurants():
    """Create multiple test restaurants for advanced testing"""
    restaurants = []
    
    restaurant_data = [
        {
            "name": "Test Italian Restaurant",
            "area": "Downtown",
            "cuisine": "Italian",
            "items": [
                {"item_name": "Pizza Margherita", "price": 250},
                {"item_name": "Pasta Carbonara", "price": 300}
            ]
        },
        {
            "name": "Test Gujarati Restaurant",
            "area": "Satellite",
            "cuisine": "Gujarati",
            "items": [
                {"item_name": "Dhokla", "price": 50},
                {"item_name": "Thepla", "price": 60}
            ]
        },
        {
            "name": "Test Chinese Restaurant",
            "area": "CG Road",
            "cuisine": "Chinese",
            "items": [
                {"item_name": "Fried Rice", "price": 180},
                {"item_name": "Manchurian", "price": 200}
            ]
        }
    ]
    
    for data in restaurant_data:
        # Clean up if exists
        existing = await Restaurant.find_one(Restaurant.name == data["name"])
        if existing:
            await existing.delete()
        
        restaurant = Restaurant(**data)
        await restaurant.insert()
        restaurants.append(restaurant)
    
    yield restaurants
    
    # Cleanup
    for restaurant in restaurants:
        try:
            await restaurant.delete()
        except:
            pass


@pytest.fixture
async def test_user_with_orders(test_user, test_restaurant):
    """Create a test user with existing orders"""
    orders = []
    
    # Create sample orders
    for i in range(3):
        order = Order(
            user_id=test_user.id,
            restaurant_name=test_restaurant.name,
            items=[
                OrderItem(
                    item_name=f"Test Item {i+1}",
                    quantity=i+1,
                    price=100.0 * (i+1)
                )
            ],
            total_price=100.0 * (i+1) * (i+1),
            status="placed"
        )
        await order.insert()
        orders.append(order)
    
    yield test_user, orders
    
    # Cleanup
    for order in orders:
        try:
            await order.delete()
        except:
            pass


@pytest.fixture
def sample_restaurant():
    """Create a test restaurant (returns fixture reference)"""
    # This is a reference fixture that points to test_restaurant
    # Don't call test_restaurant() directly, just reference it
    return None  # Will be overridden in tests that use test_restaurant


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
    try:
        await restaurant.delete()
    except:
        pass  # Already deleted


# Test data constants
TEST_VALID_EMAIL = "valid@example.com"
TEST_VALID_PASSWORD = "SecurePass123!"
TEST_INVALID_EMAIL = "not-an-email"
TEST_WEAK_PASSWORD = "123"
