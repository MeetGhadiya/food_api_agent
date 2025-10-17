"""
Pytest Configuration and Fixtures for FoodieExpress Test Suite

This conftest.py provides:
1. Session-scoped event loop for all async tests
2. One-time Beanie database initialization
3. Automatic test data cleanup between tests
4. Properly managed async HTTP clients
5. Reusable user fixtures with authentication tokens

Purpose: Eliminate "Event loop is closed" errors and ensure stable test execution
"""

import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os

from app.main import app
from app.models import User, Restaurant, Order, Review, OrderItem
from app.security import hash_password

# ==========================================================
# SESSION-SCOPED EVENT LOOP
# ==========================================================
# Create a single event loop shared by all tests

@pytest.fixture(scope="session")
def event_loop():
    """
    Create a session-scoped event loop.
    
    This is CRITICAL for Motor/Beanie compatibility - they need
    a stable event loop that doesn't close between tests.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# ==========================================================
# DATABASE INITIALIZATION (SESSION-SCOPED)
# ==========================================================
# Initialize Beanie once per session with session-scoped event loop

@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_database(event_loop):
    """
    Initialize MongoDB and Beanie ODM once for entire test session.
    
    This fixture:
    - Uses the session-scoped event loop
    - Initializes Beanie ONCE 
    - Connects to test database (food_db_test)
    - Cleans up after all tests
    
    CRITICAL: Session-scoped with explicit event_loop dependency
              to ensure Motor uses the correct, persistent event loop.
    
    Note: Uses separate test database to avoid polluting production data
    """
    # Get MongoDB URI from environment or use local default
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    
    # Create Motor client
    client = AsyncIOMotorClient(mongodb_uri)
    database = client.food_db_test
    
    # Initialize Beanie
    await init_beanie(
        database=database,
        document_models=[User, Restaurant, Order, Review]
    )
    
    print("\n✅ Test database initialized with Beanie (session-scoped)")
    
    yield database
    
    # Cleanup after all tests
    print("\n🧹 Cleaning up test database...")
    await client.drop_database("food_db_test")
    client.close()


# ==========================================================
# TEST DATA CLEANUP (FUNCTION-SCOPED)
# ==========================================================
# Automatically clean up test data after each test to ensure isolation

@pytest_asyncio.fixture(autouse=True)
async def cleanup_test_data():
    """
    Clean up test data after each test function.
    
    This ensures:
    - Test isolation (no data leakage between tests)
    - Consistent starting state for each test
    - No duplicate key errors
    - Predictable test behavior
    
    Runs automatically after EVERY test
    """
    yield  # Test runs here
    
    # Clean up all test collections
    try:
        await User.delete_all()
        await Restaurant.delete_all()
        await Order.delete_all()
        await Review.delete_all()
    except Exception as e:
        print(f"⚠️  Warning: Cleanup failed: {e}")
        # Don't fail tests if cleanup has issues


# ==========================================================
# HTTP CLIENT FIXTURES
# ==========================================================

@pytest.fixture
def client(init_test_database):
    """
    Create a synchronous HTTP client for testing FastAPI endpoints.
    
    Use this fixture for:
    - Simple synchronous tests
    - Testing non-async endpoints
    - Quick smoke tests
    
    NOTE: Depends on init_test_database to ensure Beanie is initialized.
          TestClient will skip the app's lifespan automatically in newer versions.
    
    Note: Uses TestClient which blocks on async operations
    """
    import contextlib
    
    # Create a dummy lifespan that does nothing
    @contextlib.asynccontextmanager
    async def empty_lifespan(app):
        yield
    
    # Temporarily replace the app's lifespan
    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = empty_lifespan
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Restore original lifespan
    app.router.lifespan_context = original_lifespan


@pytest_asyncio.fixture
async def async_client(init_test_database):
    """
    Create an async HTTP client for testing FastAPI endpoints.
    
    Benefits:
    - Properly manages async context
    - Uses session-scoped event loop (no closure issues)
    - Skips app lifespan to prevent double Beanie initialization
    - Clean startup/shutdown
    
    Use this fixture for:
    - Testing async endpoints
    - Database-dependent tests
    - Tests requiring authentication
    - Complex multi-step workflows
    
    NOTE: Depends on init_test_database to ensure Beanie is initialized
          BEFORE the app starts, preventing double initialization errors.
    """
    import contextlib
    
    # Create a dummy lifespan that does nothing
    # (Beanie is already initialized by init_test_database)
    @contextlib.asynccontextmanager
    async def empty_lifespan(app):
        yield
    
    # Temporarily replace the app's lifespan
    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = empty_lifespan
    
    transport = ASGITransport(app=app)
    
    try:
        async with AsyncClient(
            transport=transport, 
            base_url="http://test",
            timeout=30.0  # Increase timeout for slow tests
        ) as client:
            yield client
    finally:
        # Restore original lifespan (for next test)
        app.router.lifespan_context = original_lifespan


# ==========================================================
# USER FIXTURES
# ==========================================================

@pytest_asyncio.fixture
async def test_user():
    """
    Create a test user for authentication tests.
    
    Provides:
    - Standard user role
    - Consistent credentials (testuser/testpassword123)
    - Clean state (removes existing user if present)
    
    Use for:
    - Testing user registration/login
    - Testing protected endpoints
    - Testing user-specific operations
    """
    # Clean up any existing test user
    existing_user = await User.find_one(User.username == "testuser")
    if existing_user:
        await existing_user.delete()
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        first_name="Test",
        last_name="User",
        role="user"
    )
    await user.insert()
    yield user
    
    # Cleanup handled by cleanup_test_data fixture


@pytest_asyncio.fixture
async def test_admin():
    """
    Create a test admin user.
    
    Provides:
    - Admin role privileges
    - Consistent credentials (testadmin/adminpass123)
    - Clean state
    
    Use for:
    - Testing admin-only endpoints
    - Testing RBAC (Role-Based Access Control)
    - Testing privileged operations
    """
    existing_admin = await User.find_one(User.username == "testadmin")
    if existing_admin:
        await existing_admin.delete()
    
    admin = User(
        username="testadmin",
        email="admin@example.com",
        hashed_password=hash_password("adminpass123"),
        first_name="Test",
        last_name="Admin",
        role="admin"
    )
    await admin.insert()
    yield admin
    
    # Cleanup handled by cleanup_test_data fixture


# ==========================================================
# AUTHENTICATION TOKEN FIXTURES
# ==========================================================

@pytest.fixture
def auth_token(client, test_user):
    """
    Get JWT authentication token for a test user (synchronous).
    
    Returns: JWT access token string
    
    Use for:
    - Sync tests requiring authentication
    - Testing protected endpoints with sync client
    """
    response = client.post(
        "/users/login",
        data={
            "username": test_user.username,
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_token_async(async_client, test_user):
    """
    Get JWT authentication token for a test user (asynchronous).
    
    Returns: JWT access token string
    
    Use for:
    - Async tests requiring authentication
    - Testing protected endpoints with async_client
    - Complex multi-step authenticated workflows
    """
    response = await async_client.post(
        "/users/login",
        data={
            "username": test_user.username,
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def admin_auth_token_async(async_client, test_admin):
    """
    Get JWT authentication token for admin user (asynchronous).
    
    Returns: JWT access token string
    
    Use for:
    - Testing admin-only endpoints
    - Testing RBAC with async_client
    - Admin-privileged operations
    """
    response = await async_client.post(
        "/users/login",
        data={
            "username": test_admin.username,
            "password": "adminpass123"
        }
    )
    assert response.status_code == 200, f"Admin login failed: {response.json()}"
    return response.json()["access_token"]


# ==========================================================
# RESTAURANT FIXTURES
# ==========================================================

@pytest_asyncio.fixture
async def multiple_test_restaurants():
    """
    Create multiple test restaurants for comprehensive testing.
    
    Provides:
    - 3 restaurants with different cuisines
    - Sample menu items for each
    - Clean state (removes existing test restaurants)
    
    Use for:
    - Testing restaurant listing/filtering
    - Testing cuisine-based search
    - Testing multi-restaurant scenarios
    """
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
    
    # Cleanup handled by cleanup_test_data fixture


# ==========================================================
# ORDER FIXTURES
# ==========================================================

@pytest_asyncio.fixture
async def test_user_with_orders(test_user, test_restaurant):
    """
    Create a test user with existing order history.
    
    Provides:
    - User with 3 sample orders
    - Orders linked to test restaurant
    - Varying quantities and prices
    
    Use for:
    - Testing order history retrieval
    - Testing order-related endpoints
    - Testing user-specific order queries
    """
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
    
    # Cleanup handled by cleanup_test_data fixture


@pytest.fixture
def sample_restaurant():
    """
    Placeholder fixture for restaurant reference.
    
    Note: This is kept for backward compatibility.
    Use test_restaurant fixture directly in most cases.
    """
    return None


@pytest_asyncio.fixture
async def test_restaurant():
    """
    Create a single test restaurant.
    
    Provides:
    - Restaurant with 2 sample menu items
    - Clean state (removes existing test restaurant)
    - Consistent test data
    
    Use for:
    - Testing single restaurant operations
    - Testing menu item queries
    - Testing restaurant-specific endpoints
    """
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
    
    # Cleanup handled by cleanup_test_data fixture


# ==========================================================
# TEST DATA CONSTANTS
# ==========================================================
# Reusable constants for validation tests

TEST_VALID_EMAIL = "valid@example.com"
TEST_VALID_PASSWORD = "SecurePass123!"
TEST_INVALID_EMAIL = "not-an-email"
TEST_WEAK_PASSWORD = "123"

# ==========================================================
# NOTES FOR TEST AUTHORS
# ==========================================================
# 1. Always use @pytest_asyncio.fixture for async fixtures
# 2. Use event_loop fixture is session-scoped (shared across tests)
# 3. Database cleanup happens automatically after each test
# 4. Use async_client for async tests, client for sync tests
# 5. Authentication tokens are automatically generated from fixtures
# 6. Test isolation is guaranteed by cleanup_test_data fixture
#
# Example async test:
#   @pytest.mark.asyncio
#   async def test_something(async_client, test_user, auth_token_async):
#       response = await async_client.get("/endpoint", 
#           headers={"Authorization": f"Bearer {auth_token_async}"})
#       assert response.status_code == 200
