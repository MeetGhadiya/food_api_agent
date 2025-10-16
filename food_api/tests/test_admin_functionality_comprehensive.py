"""
Comprehensive Integration Tests for Admin Functionality (ADMIN-001 to ADMIN-010)
Aligned with TEST_PLAN_V2.txt - FoodieExpress v4.0.0

TEST COVERAGE:
- ADMIN-001: Admin creates restaurant
- ADMIN-002: User cannot create restaurant
- ADMIN-003: Admin updates restaurant
- ADMIN-004: User cannot update restaurant
- ADMIN-005: Admin deletes restaurant
- ADMIN-006: User cannot delete restaurant
- ADMIN-007: Admin accesses platform statistics
- ADMIN-008: User cannot access statistics
- ADMIN-009: Admin views all orders
- ADMIN-010: Admin views all users (without hashed passwords)
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from app.models import Restaurant, User, Order, OrderItem
from app.security import hash_password


@pytest.mark.integration
class TestAdminRestaurantManagement:
    """Comprehensive test suite for admin restaurant management (ADMIN-001 to ADMIN-006)"""
    
    @pytest.mark.asyncio
    async def test_admin_001_create_restaurant(self, async_client, test_admin):
        """
        TEST ID: ADMIN-001
        CATEGORY: Admin Functionality
        DESCRIPTION: Test that an admin can create a new restaurant
        INPUT:
            Method: POST
            URL: /restaurants/
            Headers: Authorization: Bearer <admin_token>
            Payload: {"name": "New Restaurant", "area": "Test Area", "cuisine": "Test", "items": [...]}
        EXPECTED OUTPUT:
            Status Code: 201 Created
            Response Body: New restaurant object
            Business Rule Validated: Admin can create restaurants (Rule 4.21)
        """
        # Login as admin
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_admin.username,
                "password": "adminpass123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create restaurant
        restaurant_data = {
            "name": "Admin Created Restaurant",
            "area": "Test Area",
            "cuisine": "Test Cuisine",
            "items": [
                {"item_name": "Test Dish 1", "price": 100.0},
                {"item_name": "Test Dish 2", "price": 150.0}
            ]
        }
        
        response = await async_client.post(
            "/restaurants/",
            json=restaurant_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == restaurant_data["name"]
        assert data["area"] == restaurant_data["area"]
        assert data["cuisine"] == restaurant_data["cuisine"]
        assert len(data["items"]) == 2
        
        # Cleanup
        restaurant = await Restaurant.find_one(Restaurant.name == restaurant_data["name"])
        if restaurant:
            await restaurant.delete()
    
    @pytest.mark.asyncio
    async def test_admin_002_user_cannot_create_restaurant(self, async_client, test_user):
        """
        TEST ID: ADMIN-002
        CATEGORY: Admin Functionality
        DESCRIPTION: Test that a regular user CANNOT create a new restaurant (Rule 4.21)
        INPUT:
            Method: POST
            URL: /restaurants/
            Headers: Authorization: Bearer <user_token>
            Payload: Restaurant data
        EXPECTED OUTPUT:
            Status Code: 403 Forbidden
            Response Body: "Admin privileges required"
            Business Rule Validated: RBAC - only admins can create restaurants
        """
        # Login as regular user
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to create restaurant as user
        restaurant_data = {
            "name": "User Attempted Restaurant",
            "area": "Test Area",
            "cuisine": "Test Cuisine",
            "items": [{"item_name": "Test Item", "price": 100.0}]
        }
        
        response = await async_client.post(
            "/restaurants/",
            json=restaurant_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "admin" in data["detail"].lower() or \
               "forbidden" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_admin_003_update_restaurant(self, async_client, test_admin, test_restaurant):
        """
        TEST ID: ADMIN-003
        CATEGORY: Admin Functionality
        DESCRIPTION: Test that an admin can update a restaurant
        INPUT:
            Method: PUT
            URL: /restaurants/{restaurant_name}
            Headers: Authorization: Bearer <admin_token>
            Payload: Updated restaurant data
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: Updated restaurant object
            Business Rule Validated: Admin can update restaurants
        """
        # Login as admin
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_admin.username,
                "password": "adminpass123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update restaurant
        update_data = {
            "name": test_restaurant.name,
            "area": "Updated Area",
            "cuisine": "Updated Cuisine",
            "items": [
                {"item_name": "Updated Item 1", "price": 200.0}
            ]
        }
        
        response = await async_client.put(
            f"/restaurants/{test_restaurant.name}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["area"] == "Updated Area"
        assert data["cuisine"] == "Updated Cuisine"
        
        # Restore original data
        restore_data = {
            "name": test_restaurant.name,
            "area": test_restaurant.area,
            "cuisine": test_restaurant.cuisine,
            "items": test_restaurant.items
        }
        await async_client.put(
            f"/restaurants/{test_restaurant.name}",
            json=restore_data,
            headers=headers
        )
    
    @pytest.mark.asyncio
    async def test_admin_004_user_cannot_update_restaurant(self, async_client, test_user, test_restaurant):
        """
        TEST ID: ADMIN-004
        CATEGORY: Admin Functionality
        DESCRIPTION: Test that a regular user CANNOT update a restaurant (Rule 4.21)
        INPUT:
            Method: PUT
            URL: /restaurants/{restaurant_name}
            Headers: Authorization: Bearer <user_token>
            Payload: Updated restaurant data
        EXPECTED OUTPUT:
            Status Code: 403 Forbidden
            Response Body: "Admin privileges required"
            Business Rule Validated: RBAC - only admins can update restaurants
        """
        # Login as regular user
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to update restaurant as user
        update_data = {
            "name": test_restaurant.name,
            "area": "Hacked Area",
            "cuisine": "Hacked Cuisine",
            "items": []
        }
        
        response = await async_client.put(
            f"/restaurants/{test_restaurant.name}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "admin" in data["detail"].lower() or \
               "forbidden" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_admin_005_delete_restaurant(self, async_client, test_admin):
        """
        TEST ID: ADMIN-005
        CATEGORY: Admin Functionality
        DESCRIPTION: Test that an admin can delete a restaurant
        INPUT:
            Method: DELETE
            URL: /restaurants/{restaurant_name}
            Headers: Authorization: Bearer <admin_token>
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: Success message
            Business Rule Validated: Admin can delete restaurants
        """
        # Create a restaurant to delete
        temp_restaurant = Restaurant(
            name="To Be Deleted Restaurant",
            area="Test Area",
            cuisine="Test Cuisine",
            items=[{"item_name": "Test Item", "price": 100.0}]
        )
        await temp_restaurant.insert()
        
        # Login as admin
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_admin.username,
                "password": "adminpass123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Delete restaurant
        response = await async_client.delete(
            f"/restaurants/{temp_restaurant.name}",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "deleted" in data["message"].lower() or \
               "success" in data["message"].lower()
        
        # Verify deletion
        deleted_restaurant = await Restaurant.find_one(Restaurant.name == temp_restaurant.name)
        assert deleted_restaurant is None
    
    @pytest.mark.asyncio
    async def test_admin_006_user_cannot_delete_restaurant(self, async_client, test_user, test_restaurant):
        """
        TEST ID: ADMIN-006
        CATEGORY: Admin Functionality
        DESCRIPTION: Test that a regular user CANNOT delete a restaurant (Rule 4.21)
        INPUT:
            Method: DELETE
            URL: /restaurants/{restaurant_name}
            Headers: Authorization: Bearer <user_token>
        EXPECTED OUTPUT:
            Status Code: 403 Forbidden
            Response Body: "Admin privileges required"
            Business Rule Validated: RBAC - only admins can delete restaurants
        """
        # Login as regular user
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to delete restaurant as user
        response = await async_client.delete(
            f"/restaurants/{test_restaurant.name}",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "admin" in data["detail"].lower() or \
               "forbidden" in data["detail"].lower()
        
        # Verify restaurant still exists
        existing_restaurant = await Restaurant.find_one(Restaurant.name == test_restaurant.name)
        assert existing_restaurant is not None


@pytest.mark.integration
class TestAdminDashboard:
    """Comprehensive test suite for admin dashboard (ADMIN-007 to ADMIN-010)"""
    
    @pytest.mark.asyncio
    async def test_admin_007_access_platform_statistics(self, async_client, test_admin):
        """
        TEST ID: ADMIN-007
        CATEGORY: Admin Functionality
        DESCRIPTION: Test that an admin can access platform statistics
        INPUT:
            Method: GET
            URL: /admin/stats
            Headers: Authorization: Bearer <admin_token>
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON object with platform statistics
            Business Rule Validated: Admin can view platform analytics
        """
        # Login as admin
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_admin.username,
                "password": "adminpass123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get platform stats
        response = await async_client.get("/admin/stats", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_users" in data
        assert "total_orders" in data
        assert "total_revenue" in data
        assert "orders_today" in data
        assert "revenue_today" in data
        assert "active_users_last_7_days" in data
        assert "total_reviews" in data
        assert "average_rating" in data
        
        # Validate data types
        assert isinstance(data["total_users"], int)
        assert isinstance(data["total_orders"], int)
        assert isinstance(data["total_revenue"], (int, float))
    
    @pytest.mark.asyncio
    async def test_admin_008_user_cannot_access_statistics(self, async_client, test_user):
        """
        TEST ID: ADMIN-008
        CATEGORY: Admin Functionality
        DESCRIPTION: Test that a regular user CANNOT access platform statistics (Rule 4.21)
        INPUT:
            Method: GET
            URL: /admin/stats
            Headers: Authorization: Bearer <user_token>
        EXPECTED OUTPUT:
            Status Code: 403 Forbidden
            Response Body: "Admin privileges required"
            Business Rule Validated: RBAC - only admins can view statistics
        """
        # Login as regular user
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access stats as user
        response = await async_client.get("/admin/stats", headers=headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "admin" in data["detail"].lower() or \
               "forbidden" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_admin_009_view_all_orders(self, async_client, test_admin, test_user, test_restaurant):
        """
        TEST ID: ADMIN-009
        CATEGORY: Admin Functionality
        DESCRIPTION: Test that an admin can view all orders
        INPUT:
            Method: GET
            URL: /admin/orders
            Headers: Authorization: Bearer <admin_token>
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: Array of all orders on the platform
            Business Rule Validated: Admin can view all orders for management
        """
        # Create a test order
        test_order = Order(
            user_id=test_user.id,
            restaurant_name=test_restaurant.name,
            items=[
                OrderItem(item_name="Test Item", quantity=1, price=100.0)
            ],
            total_price=100.0,
            status="placed"
        )
        await test_order.insert()
        
        try:
            # Login as admin
            login_response = await async_client.post(
                "/users/login",
                data={
                    "username": test_admin.username,
                    "password": "adminpass123"
                }
            )
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get all orders
            response = await async_client.get("/admin/orders", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            
            # Verify our test order is in the list
            order_ids = [str(o["id"]) for o in data]
            assert str(test_order.id) in order_ids
        finally:
            # Cleanup
            await test_order.delete()
    
    @pytest.mark.asyncio
    async def test_admin_010_view_all_users_no_passwords(self, async_client, test_admin):
        """
        TEST ID: ADMIN-010
        CATEGORY: Admin Functionality
        DESCRIPTION: Test that an admin can view all users without hashed_password field (Rule 4.23)
        INPUT:
            Method: GET
            URL: /admin/users
            Headers: Authorization: Bearer <admin_token>
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: Array of user objects WITHOUT hashed_password field
            Business Rule Validated: Admin can view users, passwords excluded for security
        """
        # Login as admin
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_admin.username,
                "password": "adminpass123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all users
        response = await async_client.get("/admin/users", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Should return at least the admin user"
        
        # Verify structure and security
        for user in data:
            assert "id" in user
            assert "username" in user
            assert "email" in user
            assert "role" in user
            # CRITICAL: Passwords should NEVER be returned
            assert "password" not in str(user).lower() or \
                   "hashed_password" not in str(user).lower()


@pytest.mark.integration
class TestAdminRBACEdgeCases:
    """Additional RBAC edge case tests for admin functionality"""
    
    @pytest.mark.asyncio
    async def test_admin_endpoints_require_authentication(self, async_client):
        """
        Test that admin endpoints require authentication
        """
        admin_endpoints = [
            ("/restaurants/", "POST"),
            ("/admin/stats", "GET"),
            ("/admin/orders", "GET"),
            ("/admin/users", "GET")
        ]
        
        for endpoint, method in admin_endpoints:
            if method == "GET":
                response = await async_client.get(endpoint)
            elif method == "POST":
                response = await async_client.post(endpoint, json={})
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
                f"{method} {endpoint} should require authentication"
    
    @pytest.mark.asyncio
    async def test_regular_user_cannot_access_any_admin_endpoint(self, async_client, test_user):
        """
        Comprehensive test that regular users are blocked from all admin endpoints
        """
        # Login as regular user
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test all admin endpoints
        admin_endpoints = [
            ("/admin/stats", "GET"),
            ("/admin/orders", "GET"),
            ("/admin/users", "GET"),
            ("/restaurants/", "POST")
        ]
        
        for endpoint, method in admin_endpoints:
            if method == "GET":
                response = await async_client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await async_client.post(
                    endpoint,
                    json={"name": "Test", "area": "Test", "cuisine": "Test", "items": []},
                    headers=headers
                )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN, \
                f"Regular user should be forbidden from {method} {endpoint}"
