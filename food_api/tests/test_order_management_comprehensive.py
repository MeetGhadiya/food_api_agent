"""
Comprehensive Integration Tests for Order Management (ORDER-001 to ORDER-010)
Aligned with TEST_PLAN_V2.txt - FoodieExpress v4.0.0

TEST COVERAGE:
- ORDER-001: Valid multi-item order creation
- ORDER-002: Order for non-existent restaurant
- ORDER-003: Invalid quantity (0)
- ORDER-004: Excessive quantity (101)
- ORDER-005: Empty items array
- ORDER-006: More than 50 items
- ORDER-007: Negative price
- ORDER-008: Get user order history
- ORDER-009: Get own specific order
- ORDER-010: Access another user's order (IDOR)
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from app.models import Restaurant, User, Order, OrderItem
from app.security import hash_password


@pytest.mark.integration
class TestOrderCreation:
    """Comprehensive test suite for order creation (ORDER-001 to ORDER-007)"""
    
    @pytest.mark.asyncio
    async def test_order_001_create_valid_multiitem_order(self, async_client, test_user, test_restaurant):
        """
        TEST ID: ORDER-001
        CATEGORY: Order Management
        DESCRIPTION: Test successful creation of a valid, multi-item order
        INPUT:
            Method: POST
            URL: /orders/
            Headers: Authorization: Bearer <token>
            Payload: {
                "restaurant_name": "Test Restaurant",
                "items": [
                    {"item_name": "Item1", "quantity": 2, "price": 100},
                    {"item_name": "Item2", "quantity": 1, "price": 150}
                ]
            }
        EXPECTED OUTPUT:
            Status Code: 201 Created
            Response Body: Full order object with calculated total_price (350)
            Business Rule Validated: Multi-item order placement
        """
        # Login to get token
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create order
        order_data = {
            "restaurant_name": test_restaurant.name,
            "items": [
                {"item_name": "Test Item 1", "quantity": 2, "price": 100.0},
                {"item_name": "Test Item 2", "quantity": 1, "price": 150.0}
            ]
        }
        
        response = await async_client.post("/orders/", json=order_data, headers=headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["restaurant_name"] == test_restaurant.name
        assert len(data["items"]) == 2
        # Verify total price calculation: (2 * 100) + (1 * 150) = 350
        assert data["total_price"] == 350.0
        assert data["status"] == "placed"
        assert "id" in data
        assert "order_date" in data
        
        # Cleanup
        from beanie import PydanticObjectId
        order = await Order.get(PydanticObjectId(data["id"]))
        if order:
            await order.delete()
    
    @pytest.mark.asyncio
    async def test_order_002_nonexistent_restaurant(self, async_client, test_user):
        """
        TEST ID: ORDER-002
        CATEGORY: Order Management
        DESCRIPTION: Test creating an order for a non-existent restaurant (Rule 4.5)
        INPUT:
            Method: POST
            URL: /orders/
            Headers: Authorization: Bearer <token>
            Payload: {"restaurant_name": "NonExistentRestaurant", "items": [...]}
        EXPECTED OUTPUT:
            Status Code: 404 Not Found
            Response Body: "Restaurant not found"
            Business Rule Validated: Restaurant existence validation
        """
        # Login to get token
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create order for non-existent restaurant
        order_data = {
            "restaurant_name": "NonExistentRestaurant12345",
            "items": [
                {"item_name": "Test Item", "quantity": 1, "price": 100.0}
            ]
        }
        
        response = await async_client.post("/orders/", json=order_data, headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_order_003_invalid_quantity_zero(self, async_client, test_user, test_restaurant):
        """
        TEST ID: ORDER-003
        CATEGORY: Order Management
        DESCRIPTION: Test creating an order with an invalid quantity of 0 (Rule 4.1)
        INPUT:
            Method: POST
            URL: /orders/
            Headers: Authorization: Bearer <token>
            Payload: {"items": [{"item_name": "Item", "quantity": 0, "price": 100}]}
        EXPECTED OUTPUT:
            Status Code: 422 Unprocessable Entity
            Response Body: Validation error
            Business Rule Validated: Quantity must be at least 1
        """
        # Login to get token
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create order with quantity 0
        order_data = {
            "restaurant_name": test_restaurant.name,
            "items": [
                {"item_name": "Test Item", "quantity": 0, "price": 100.0}
            ]
        }
        
        response = await async_client.post("/orders/", json=order_data, headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_order_004_excessive_quantity(self, async_client, test_user, test_restaurant):
        """
        TEST ID: ORDER-004
        CATEGORY: Order Management
        DESCRIPTION: Test creating an order with an excessive quantity of 101 (Rule 4.2)
        INPUT:
            Method: POST
            URL: /orders/
            Headers: Authorization: Bearer <token>
            Payload: {"items": [{"item_name": "Item", "quantity": 101, "price": 100}]}
        EXPECTED OUTPUT:
            Status Code: 422 Unprocessable Entity
            Response Body: Validation error
            Business Rule Validated: Maximum quantity per item is 100
        """
        # Login to get token
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create order with quantity 101
        order_data = {
            "restaurant_name": test_restaurant.name,
            "items": [
                {"item_name": "Test Item", "quantity": 101, "price": 100.0}
            ]
        }
        
        response = await async_client.post("/orders/", json=order_data, headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_order_005_empty_items_array(self, async_client, test_user, test_restaurant):
        """
        TEST ID: ORDER-005
        CATEGORY: Order Management
        DESCRIPTION: Test creating an order with an empty items array
        INPUT:
            Method: POST
            URL: /orders/
            Headers: Authorization: Bearer <token>
            Payload: {"restaurant_name": "Test", "items": []}
        EXPECTED OUTPUT:
            Status Code: 422 Unprocessable Entity
            Response Body: Validation error
            Business Rule Validated: Order must contain at least one item
        """
        # Login to get token
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create order with empty items
        order_data = {
            "restaurant_name": test_restaurant.name,
            "items": []
        }
        
        response = await async_client.post("/orders/", json=order_data, headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_order_006_too_many_items(self, async_client, test_user, test_restaurant):
        """
        TEST ID: ORDER-006
        CATEGORY: Order Management
        DESCRIPTION: Test creating an order with more than 50 line items (Rule 4.3)
        INPUT:
            Method: POST
            URL: /orders/
            Headers: Authorization: Bearer <token>
            Payload: {"items": [51 items]}
        EXPECTED OUTPUT:
            Status Code: 422 Unprocessable Entity
            Response Body: Validation error
            Business Rule Validated: Maximum 50 items per order
        """
        # Login to get token
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create order with 51 items
        items = [
            {"item_name": f"Item {i}", "quantity": 1, "price": 100.0}
            for i in range(51)
        ]
        order_data = {
            "restaurant_name": test_restaurant.name,
            "items": items
        }
        
        response = await async_client.post("/orders/", json=order_data, headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_order_007_negative_price(self, async_client, test_user, test_restaurant):
        """
        TEST ID: ORDER-007
        CATEGORY: Order Management
        DESCRIPTION: Test creating an order with a negative price (Rule 4.4)
        INPUT:
            Method: POST
            URL: /orders/
            Headers: Authorization: Bearer <token>
            Payload: {"items": [{"item_name": "Item", "quantity": 1, "price": -50}]}
        EXPECTED OUTPUT:
            Status Code: 422 Unprocessable Entity
            Response Body: Validation error
            Business Rule Validated: Price must be non-negative
        """
        # Login to get token
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create order with negative price
        order_data = {
            "restaurant_name": test_restaurant.name,
            "items": [
                {"item_name": "Test Item", "quantity": 1, "price": -50.0}
            ]
        }
        
        response = await async_client.post("/orders/", json=order_data, headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data


@pytest.mark.integration
class TestOrderRetrieval:
    """Comprehensive test suite for order retrieval (ORDER-008 to ORDER-010)"""
    
    @pytest.mark.asyncio
    async def test_order_008_get_user_order_history(self, async_client, test_user, test_restaurant):
        """
        TEST ID: ORDER-008
        CATEGORY: Order Management
        DESCRIPTION: Test successful retrieval of the user's own order history
        INPUT:
            Method: GET
            URL: /orders/
            Headers: Authorization: Bearer <token>
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON array of the user's past orders
            Business Rule Validated: User can view their own order history
        """
        # Login to get token
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a test order
        order = Order(
            user_id=test_user.id,
            restaurant_name=test_restaurant.name,
            items=[
                OrderItem(item_name="Test Item", quantity=1, price=100.0)
            ],
            total_price=100.0,
            status="placed"
        )
        await order.insert()
        
        try:
            # Get order history
            response = await async_client.get("/orders/", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            
            # Should contain our test order
            order_ids = [str(o["id"]) for o in data]
            assert str(order.id) in order_ids
        finally:
            # Cleanup
            await order.delete()
    
    @pytest.mark.asyncio
    async def test_order_009_get_own_specific_order(self, async_client, test_user, test_restaurant):
        """
        TEST ID: ORDER-009
        CATEGORY: Order Management
        DESCRIPTION: Test successful retrieval of a specific order owned by the user
        INPUT:
            Method: GET
            URL: /orders/{order_id}
            Headers: Authorization: Bearer <token>
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: Full order object
            Business Rule Validated: User can view their own order details
        """
        # Login to get token
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a test order
        order = Order(
            user_id=test_user.id,
            restaurant_name=test_restaurant.name,
            items=[
                OrderItem(item_name="Test Item", quantity=2, price=150.0)
            ],
            total_price=300.0,
            status="placed"
        )
        await order.insert()
        
        try:
            # Get specific order
            response = await async_client.get(f"/orders/{str(order.id)}", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == str(order.id)
            assert data["restaurant_name"] == test_restaurant.name
            assert data["total_price"] == 300.0
        finally:
            # Cleanup
            await order.delete()
    
    @pytest.mark.asyncio
    async def test_order_010_access_another_users_order_idor(self, async_client, test_restaurant):
        """
        TEST ID: ORDER-010
        CATEGORY: Order Management
        DESCRIPTION: Test failure when trying to retrieve another user's order (Rule 4.35 / IDOR)
        INPUT:
            Method: GET
            URL: /orders/{order_id} (order belongs to User B)
            Headers: Authorization: Bearer <User A token>
        EXPECTED OUTPUT:
            Status Code: 403 Forbidden
            Response Body: "You don't have permission to view this order"
            Business Rule Validated: IDOR protection - users cannot access other users' orders
        """
        # Create User A
        user_a = User(
            username="user_a_idor",
            email="usera@example.com",
            hashed_password=hash_password("testpass123"),
            role="user"
        )
        await user_a.insert()
        
        # Create User B
        user_b = User(
            username="user_b_idor",
            email="userb@example.com",
            hashed_password=hash_password("testpass123"),
            role="user"
        )
        await user_b.insert()
        
        try:
            # Create an order for User B
            order_b = Order(
                user_id=user_b.id,
                restaurant_name=test_restaurant.name,
                items=[
                    OrderItem(item_name="Test Item", quantity=1, price=100.0)
                ],
                total_price=100.0,
                status="placed"
            )
            await order_b.insert()
            
            # Login as User A
            login_response = await async_client.post(
                "/users/login",
                data={
                    "username": user_a.username,
                    "password": "testpass123"
                }
            )
            token_a = login_response.json()["access_token"]
            headers_a = {"Authorization": f"Bearer {token_a}"}
            
            # Try to access User B's order as User A
            response = await async_client.get(
                f"/orders/{str(order_b.id)}", 
                headers=headers_a
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
            data = response.json()
            assert "permission" in data["detail"].lower() or \
                   "forbidden" in data["detail"].lower()
            
            # Cleanup order
            await order_b.delete()
        finally:
            # Cleanup users
            await user_a.delete()
            await user_b.delete()


@pytest.mark.integration
class TestOrderEdgeCases:
    """Additional edge case tests for order management"""
    
    @pytest.mark.asyncio
    async def test_order_without_authentication(self, async_client, test_restaurant):
        """
        Test that order creation requires authentication
        """
        order_data = {
            "restaurant_name": test_restaurant.name,
            "items": [
                {"item_name": "Test Item", "quantity": 1, "price": 100.0}
            ]
        }
        
        response = await async_client.post("/orders/", json=order_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "not authenticated" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_order_total_price_calculation(self, async_client, test_user, test_restaurant):
        """
        Test that total_price is correctly calculated for multi-item orders
        """
        # Login to get token
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create order with multiple items
        order_data = {
            "restaurant_name": test_restaurant.name,
            "items": [
                {"item_name": "Item 1", "quantity": 3, "price": 50.0},   # 150
                {"item_name": "Item 2", "quantity": 2, "price": 75.0},   # 150
                {"item_name": "Item 3", "quantity": 1, "price": 200.0}   # 200
            ]
        }
        
        response = await async_client.post("/orders/", json=order_data, headers=headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # Total: 150 + 150 + 200 = 500
        assert data["total_price"] == 500.0
        
        # Cleanup
        from beanie import PydanticObjectId
        order = await Order.get(PydanticObjectId(data["id"]))
        if order:
            await order.delete()
