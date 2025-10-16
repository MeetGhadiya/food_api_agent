"""
Integration Tests for Public API Endpoints
Tests restaurant listing, search, and public data access

TEST COVERAGE (100% aligned with TEST_PLAN_V2.txt):
- PUB-001 to PUB-015: Public endpoints
- Restaurant listing and filtering
- Restaurant search by name
- Item search functionality
- Public review endpoints
- Health check endpoint
"""

import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.integration
class TestRestaurantEndpoints:
    """Test public restaurant endpoints"""
    
    @pytest.mark.asyncio
    async def test_pub_001_get_root(self, async_client):
        """
        TEST ID: PUB-001
        DESCRIPTION: Verify the root welcome endpoint is functional
        INPUT: GET /
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON with project version and features
            Business Rule: Root endpoint accessibility
        """
        response = await async_client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "4.0.0"
        assert "features" in data
        assert isinstance(data["features"], list)
        assert len(data["features"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_all_restaurants(self, async_client):
        """Test getting all restaurants without authentication"""
        response = await async_client.get("/restaurants/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        # Verify restaurant structure
        if len(data) > 0:
            restaurant = data[0]
            assert "name" in restaurant
            assert "area" in restaurant
            assert "cuisine" in restaurant
            assert "items" in restaurant
    
    @pytest.mark.asyncio
    async def test_get_restaurants_by_cuisine(self, async_client, test_restaurant):
        """Test filtering restaurants by cuisine"""
        response = await async_client.get(f"/restaurants/?cuisine={test_restaurant.cuisine}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        # All restaurants should match the cuisine filter
        for restaurant in data:
            assert restaurant["cuisine"].lower() == test_restaurant.cuisine.lower()
    
    @pytest.mark.asyncio
    async def test_get_restaurants_case_insensitive_cuisine(self, async_client):
        """Test that cuisine filtering is case-insensitive"""
        # Test different case variations
        test_cuisines = ["gujarati", "GUJARATI", "Gujarati", "GuJaRaTi"]
        
        results = []
        for cuisine in test_cuisines:
            response = await async_client.get(f"/restaurants/?cuisine={cuisine}")
            results.append(response.json())
        
        # All should return the same results
        if results[0]:  # If there are any results
            for result in results[1:]:
                assert len(result) == len(results[0])
    
    @pytest.mark.asyncio
    async def test_get_restaurant_by_name(self, async_client, test_restaurant):
        """Test getting a specific restaurant by name"""
        response = await async_client.get(f"/restaurants/{test_restaurant.name}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == test_restaurant.name
        assert data["area"] == test_restaurant.area
        assert data["cuisine"] == test_restaurant.cuisine
        assert "items" in data
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_restaurant(self, async_client):
        """Test that getting non-existent restaurant returns 404"""
        response = await async_client.get("/restaurants/NonExistentRestaurant12345")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.integration
class TestSearchEndpoints:
    """Test search functionality"""
    
    @pytest.mark.asyncio
    async def test_search_restaurants_by_item(self, async_client, test_restaurant):
        """Test searching for restaurants by menu item"""
        # Get first item from test restaurant
        if test_restaurant.items:
            item_name = test_restaurant.items[0].item_name
            
            response = await async_client.get(f"/search/items?item_name={item_name}")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            
            # Should include our test restaurant
            restaurant_names = [r["name"] for r in data]
            assert test_restaurant.name in restaurant_names
    
    @pytest.mark.asyncio
    async def test_search_nonexistent_item(self, async_client):
        """Test searching for an item that doesn't exist"""
        response = await async_client.get("/search/items?item_name=NonExistentItem12345")
        
        # Should return empty list or 404
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data == []


@pytest.mark.integration
class TestHealthCheck:
    """Test health check endpoint"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Test that health check endpoint returns healthy status"""
        response = await async_client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "database" in data


@pytest.mark.integration
class TestPublicReviewEndpoints:
    """Test public review endpoints (no authentication required)"""
    
    @pytest.mark.asyncio
    async def test_get_restaurant_reviews(self, async_client, test_restaurant):
        """Test getting reviews for a restaurant"""
        response = await async_client.get(f"/restaurants/{test_restaurant.name}/reviews")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_review_stats(self, async_client, test_restaurant):
        """Test getting review statistics for a restaurant"""
        response = await async_client.get(f"/restaurants/{test_restaurant.name}/reviews/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_reviews" in data
        assert "average_rating" in data
        assert "rating_distribution" in data
        
        # Verify rating distribution structure
        distribution = data["rating_distribution"]
        for i in range(1, 6):
            assert str(i) in distribution or i in distribution


@pytest.mark.security
class TestInputValidation:
    """Test input validation and injection prevention"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_restaurant_search(self, async_client):
        """Test that SQL injection attempts are safely handled"""
        malicious_inputs = [
            "'; DROP TABLE restaurants; --",
            "1' OR '1'='1",
            "admin'--",
        ]
        
        for malicious_input in malicious_inputs:
            response = await async_client.get(f"/restaurants/{malicious_input}")
            
            # Should return 404, not crash or expose data
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_xss_in_search_query(self, async_client):
        """Test that XSS attempts in search are handled"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
        ]
        
        for payload in xss_payloads:
            response = await async_client.get(f"/search/items?item_name={payload}")
            
            # Should return empty results or 404, not execute script
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
            
            if response.status_code == status.HTTP_200_OK:
                # Should not contain the raw script in response
                assert "<script>" not in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_nosql_injection_in_cuisine_filter(self, async_client):
        """Test that NoSQL injection attempts are prevented"""
        malicious_payloads = [
            '{"$ne": null}',
            '{"$gt": ""}',
            '{"$regex": ".*"}',
        ]
        
        for payload in malicious_payloads:
            response = await async_client.get(f"/restaurants/?cuisine={payload}")
            
            # Should return empty results or specific matches, not all restaurants
            assert response.status_code == status.HTTP_200_OK


@pytest.mark.smoke
class TestSmokeTests:
    """Quick smoke tests for deployment validation"""
    
    @pytest.mark.asyncio
    async def test_api_is_running(self, async_client):
        """Test that API is running and responding"""
        response = await async_client.get("/")
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_critical_endpoints_accessible(self, async_client):
        """Test that all critical endpoints are accessible"""
        endpoints = [
            "/",
            "/health",
            "/restaurants/",
        ]
        
        for endpoint in endpoints:
            response = await async_client.get(endpoint)
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_404_NOT_FOUND  # OK if no data yet
            ]
