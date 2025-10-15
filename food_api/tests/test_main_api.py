"""
Integration Tests for FastAPI Main Application
Tests API endpoints with real HTTP requests
"""

import pytest
from httpx import AsyncClient


class TestPublicEndpoints:
    """Test public endpoints that don't require authentication"""
    
    @pytest.mark.asyncio
    async def test_read_root(self, async_client):
        """Test the root endpoint returns welcome message"""
        response = await async_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "2.0.0"
    
    @pytest.mark.asyncio
    async def test_get_all_restaurants(self, async_client):
        """Test getting all restaurants without authentication"""
        response = await async_client.get("/restaurants/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_restaurants_by_cuisine(self, async_client):
        """Test filtering restaurants by cuisine"""
        response = await async_client.get("/restaurants/?cuisine=Gujarati")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All returned restaurants should have Gujarati cuisine
        for restaurant in data:
            assert restaurant.get("cuisine", "").lower() == "gujarati"
    
    @pytest.mark.asyncio
    async def test_get_restaurant_by_name(self, async_client, test_restaurant):
        """Test getting a specific restaurant by name"""
        response = await async_client.get(f"/restaurants/{test_restaurant.name}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_restaurant.name
        assert data["area"] == test_restaurant.area
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_restaurant(self, async_client):
        """Test that getting a non-existent restaurant returns 404"""
        response = await async_client.get("/restaurants/NonExistentRestaurant")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUserAuthenticationFlow:
    """Test user registration and authentication endpoints"""
    
    @pytest.mark.asyncio
    async def test_register_new_user(self, async_client):
        """Test registering a new user"""
        new_user_data = {
            "username": "newuser123",
            "email": "newuser@example.com",
            "password": "SecurePassword123!"
        }
        
        response = await async_client.post("/users/register", json=new_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == new_user_data["username"]
        assert data["email"] == new_user_data["email"]
        assert "password" not in data  # Password should not be in response
        assert "hashed_password" not in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, async_client, test_user):
        """Test that registering with a duplicate username fails"""
        duplicate_user_data = {
            "username": test_user.username,  # Already exists
            "email": "different@example.com",
            "password": "AnotherPass123!"
        }
        
        response = await async_client.post("/users/register", json=duplicate_user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_with_valid_credentials(self, async_client, test_user):
        """Test logging in with correct credentials"""
        response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    @pytest.mark.asyncio
    async def test_login_with_invalid_password(self, async_client, test_user):
        """Test that login fails with wrong password"""
        response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_with_nonexistent_user(self, async_client):
        """Test that login fails for non-existent user"""
        response = await async_client.post(
            "/users/login",
            data={
                "username": "nonexistentuser",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Test endpoints that require authentication"""
    
    @pytest.mark.asyncio
    async def test_create_order_without_auth(self, async_client):
        """Test that creating an order without authentication fails"""
        order_data = {
            "restaurant_name": "Test Restaurant",
            "items": [
                {"item_name": "Test Item", "quantity": 1, "price": 100}
            ]
        }
        
        response = await async_client.post("/orders/", json=order_data)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_order_with_auth(self, async_client, auth_token, test_restaurant):
        """Test creating an order with valid authentication"""
        order_data = {
            "restaurant_name": test_restaurant.name,
            "items": [
                {"item_name": "Test Item 1", "quantity": 2, "price": 100}
            ]
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = await async_client.post("/orders/", json=order_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["restaurant_name"] == test_restaurant.name
        assert "id" in data
        assert data["total_price"] == 200  # 2 * 100
    
    @pytest.mark.asyncio
    async def test_get_user_orders(self, async_client, auth_token):
        """Test getting order history for authenticated user"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = await async_client.get("/orders/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_add_review_with_auth(self, async_client, auth_token, test_restaurant):
        """Test adding a review with authentication"""
        review_data = {
            "rating": 5,
            "comment": "Excellent food and service!"
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = await async_client.post(
            f"/restaurants/{test_restaurant.name}/reviews",
            json=review_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == review_data["comment"]
    
    @pytest.mark.asyncio
    async def test_add_review_without_auth(self, async_client, test_restaurant):
        """Test that adding a review without authentication fails"""
        review_data = {
            "rating": 5,
            "comment": "Great food!"
        }
        
        response = await async_client.post(
            f"/restaurants/{test_restaurant.name}/reviews",
            json=review_data
        )
        
        assert response.status_code == 401


class TestReviewEndpoints:
    """Test review-related endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_reviews_for_restaurant(self, async_client, test_restaurant):
        """Test getting all reviews for a restaurant"""
        response = await async_client.get(f"/restaurants/{test_restaurant.name}/reviews")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_review_stats(self, async_client, test_restaurant):
        """Test getting review statistics for a restaurant"""
        response = await async_client.get(f"/restaurants/{test_restaurant.name}/reviews/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_reviews" in data
        assert "average_rating" in data
        assert "rating_distribution" in data


class TestItemSearch:
    """Test the item search endpoint"""
    
    @pytest.mark.asyncio
    async def test_search_items_basic(self, async_client):
        """Test basic item search functionality"""
        response = await async_client.get("/search/items?item_name=Pizza")
        
        assert response.status_code in [200, 404]  # May or may not find results
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_search_items_case_insensitive(self, async_client, test_restaurant):
        """Test that item search is case-insensitive"""
        # Test with different cases
        response1 = await async_client.get("/search/items?item_name=test item 1")
        response2 = await async_client.get("/search/items?item_name=TEST ITEM 1")
        response3 = await async_client.get("/search/items?item_name=Test Item 1")
        
        # All should return the same status code
        assert response1.status_code == response2.status_code == response3.status_code


@pytest.mark.security
class TestSecurityVulnerabilities:
    """Security-focused integration tests"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_restaurant_search(self, async_client):
        """Test that SQL injection attempts are handled safely"""
        malicious_inputs = [
            "'; DROP TABLE restaurants; --",
            "1' OR '1'='1",
            "<script>alert('XSS')</script>"
        ]
        
        for malicious_input in malicious_inputs:
            response = await async_client.get(f"/restaurants/{malicious_input}")
            # Should return 404, not cause an error
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, async_client):
        """Test that invalid JWT tokens are rejected"""
        invalid_tokens = [
            "invalid.token.here",
            "Bearer fake_token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid"
        ]
        
        for invalid_token in invalid_tokens:
            headers = {"Authorization": f"Bearer {invalid_token}"}
            response = await async_client.get("/orders/", headers=headers)
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_xss_in_review_comment(self, async_client, auth_token, test_restaurant):
        """Test that XSS attempts in reviews are handled"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ]
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        for payload in xss_payloads:
            review_data = {
                "rating": 5,
                "comment": payload
            }
            
            response = await async_client.post(
                f"/restaurants/{test_restaurant.name}/reviews",
                json=review_data,
                headers=headers
            )
            
            # Should either succeed with sanitized content or be rejected
            assert response.status_code in [200, 400, 422]


@pytest.mark.slow
class TestPerformance:
    """Performance-related tests"""
    
    @pytest.mark.asyncio
    async def test_restaurant_list_response_time(self, async_client):
        """Test that restaurant listing responds quickly"""
        import time
        
        start = time.time()
        response = await async_client.get("/restaurants/")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond within 1 second
    
    @pytest.mark.asyncio
    async def test_concurrent_order_creation(self, async_client, auth_token, test_restaurant):
        """Test handling multiple concurrent order requests"""
        import asyncio
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        order_data = {
            "restaurant_name": test_restaurant.name,
            "items": [{"item_name": "Test Item 1", "quantity": 1, "price": 100}]
        }
        
        # Create 10 concurrent requests
        tasks = [
            async_client.post("/orders/", json=order_data, headers=headers)
            for _ in range(10)
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed (or at least not crash)
        for response in responses:
            if not isinstance(response, Exception):
                assert response.status_code in [200, 201]
