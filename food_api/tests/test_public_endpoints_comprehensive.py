"""
Comprehensive Integration Tests for Public API Endpoints (PUB-001 to PUB-015)
Aligned with TEST_PLAN_V2.txt - FoodieExpress v4.0.0

TEST COVERAGE:
- PUB-001: Root welcome endpoint
- PUB-002: Get all restaurants without filters
- PUB-003: Case-insensitive cuisine filtering
- PUB-004: Cuisine with no restaurants
- PUB-005: Get specific existing restaurant
- PUB-006: Get non-existent restaurant
- PUB-007: Search for existing item
- PUB-008: Search for non-existent item
- PUB-009: Search without required parameter
- PUB-010: Get restaurant reviews
- PUB-011: Get reviews for non-existent restaurant
- PUB-012: Review pagination (limit)
- PUB-013: Review pagination (skip)
- PUB-014: Review statistics
- PUB-015: Health check endpoint
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from app.models import Restaurant, Review, User
from app.security import hash_password


@pytest.mark.integration
class TestPublicEndpoints:
    """Comprehensive test suite for all public endpoints"""
    
    @pytest.mark.asyncio
    async def test_pub_001_root_endpoint(self, async_client):
        """
        TEST ID: PUB-001
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify the root welcome endpoint is functional
        INPUT:
            Method: GET
            URL: /
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON with project version "4.0.0" and features list
            Business Rule Validated: Root endpoint accessibility
        """
        response = await async_client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data, "Response should contain welcome message"
        assert "version" in data, "Response should contain version"
        assert data["version"] == "4.0.0", "Version should be 4.0.0"
        assert "features" in data, "Response should contain features list"
        assert isinstance(data["features"], list), "Features should be a list"
        assert len(data["features"]) > 0, "Features list should not be empty"
    
    @pytest.mark.asyncio
    async def test_pub_002_get_all_restaurants(self, async_client, test_restaurant):
        """
        TEST ID: PUB-002
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify retrieval of all restaurants without filters
        INPUT:
            Method: GET
            URL: /restaurants/
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON array of all restaurant objects
            Business Rule Validated: Public restaurant listing
        """
        response = await async_client.get("/restaurants/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        # Verify restaurant structure
        if len(data) > 0:
            restaurant = data[0]
            assert "name" in restaurant, "Restaurant should have name"
            assert "area" in restaurant, "Restaurant should have area"
            assert "cuisine" in restaurant, "Restaurant should have cuisine"
            assert "items" in restaurant, "Restaurant should have items"
    
    @pytest.mark.asyncio
    async def test_pub_003_filter_by_cuisine_gujarati(self, async_client):
        """
        TEST ID: PUB-003
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify case-insensitive cuisine filtering
        INPUT:
            Method: GET
            URL: /restaurants/?cuisine=gujarati
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON array of restaurants with cuisine "Gujarati"
            Business Rule Validated: Case-insensitive cuisine filtering
        """
        # Create a test restaurant with Gujarati cuisine
        gujarati_restaurant = Restaurant(
            name="Gujarati Test Restaurant",
            area="Test Area",
            cuisine="Gujarati",
            items=[{"item_name": "Dhokla", "price": 50}]
        )
        await gujarati_restaurant.insert()
        
        try:
            response = await async_client.get("/restaurants/?cuisine=gujarati")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            
            # All restaurants should have Gujarati cuisine (case-insensitive)
            for restaurant in data:
                assert restaurant["cuisine"].lower() == "gujarati", \
                    f"Expected Gujarati cuisine, got {restaurant['cuisine']}"
        finally:
            # Cleanup
            await gujarati_restaurant.delete()
    
    @pytest.mark.asyncio
    async def test_pub_004_filter_by_nonexistent_cuisine(self, async_client):
        """
        TEST ID: PUB-004
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify filtering for a cuisine with no restaurants
        INPUT:
            Method: GET
            URL: /restaurants/?cuisine=thai
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: Empty JSON array []
            Business Rule Validated: Empty results for non-existent cuisine
        """
        response = await async_client.get("/restaurants/?cuisine=thai")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) == 0, "Should return empty array for non-existent cuisine"
    
    @pytest.mark.asyncio
    async def test_pub_005_get_specific_restaurant(self, async_client, test_restaurant):
        """
        TEST ID: PUB-005
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify retrieval of a specific, existing restaurant by name
        INPUT:
            Method: GET
            URL: /restaurants/{restaurant_name}
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: Full JSON object for the restaurant
            Business Rule Validated: Retrieve specific restaurant
        """
        response = await async_client.get(f"/restaurants/{test_restaurant.name}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == test_restaurant.name
        assert data["area"] == test_restaurant.area
        assert data["cuisine"] == test_restaurant.cuisine
        assert "items" in data
        assert isinstance(data["items"], list)
    
    @pytest.mark.asyncio
    async def test_pub_006_get_nonexistent_restaurant(self, async_client):
        """
        TEST ID: PUB-006
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify failure when retrieving a non-existent restaurant
        INPUT:
            Method: GET
            URL: /restaurants/NonExistentCafe
        EXPECTED OUTPUT:
            Status Code: 404 Not Found
            Response Body: Error detail "Restaurant 'NonExistentCafe' not found"
            Business Rule Validated: Proper 404 handling
        """
        response = await async_client.get("/restaurants/NonExistentCafe")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()
        assert "NonExistentCafe" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_pub_007_search_existing_item(self, async_client, test_restaurant):
        """
        TEST ID: PUB-007
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify item search for an item that exists
        INPUT:
            Method: GET
            URL: /search/items?item_name=Pizza (or test item)
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON array of restaurants serving the item
            Business Rule Validated: Item search functionality
        """
        # Use an item from test_restaurant
        item_name = test_restaurant.items[0].item_name
        
        response = await async_client.get(f"/search/items?item_name={item_name}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        # Should include our test restaurant
        restaurant_names = [r["name"] for r in data]
        assert test_restaurant.name in restaurant_names
    
    @pytest.mark.asyncio
    async def test_pub_008_search_nonexistent_item(self, async_client):
        """
        TEST ID: PUB-008
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify item search for an item that does not exist
        INPUT:
            Method: GET
            URL: /search/items?item_name=Sushi
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: Empty JSON array []
            Business Rule Validated: Empty results for non-existent item
        """
        response = await async_client.get("/search/items?item_name=NonExistentSushi123")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) == 0, "Should return empty array for non-existent item"
    
    @pytest.mark.asyncio
    async def test_pub_009_search_missing_parameter(self, async_client):
        """
        TEST ID: PUB-009
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify item search fails without the required parameter
        INPUT:
            Method: GET
            URL: /search/items (no item_name parameter)
        EXPECTED OUTPUT:
            Status Code: 422 Unprocessable Entity
            Response Body: Validation error
            Business Rule Validated: Required parameter validation
        """
        response = await async_client.get("/search/items")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_pub_010_get_restaurant_reviews(self, async_client, test_restaurant, test_user):
        """
        TEST ID: PUB-010
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify retrieval of reviews for an existing restaurant
        INPUT:
            Method: GET
            URL: /restaurants/{restaurant_name}/reviews
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON array of review objects
            Business Rule Validated: Public review access
        """
        # Create a test review
        review = Review(
            user_id=test_user.id,
            username=test_user.username,
            restaurant_name=test_restaurant.name,
            rating=5,
            comment="Great food! Very delicious and authentic."
        )
        await review.insert()
        
        try:
            response = await async_client.get(f"/restaurants/{test_restaurant.name}/reviews")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            
            # Should contain our test review
            if len(data) > 0:
                review_obj = data[0]
                assert "rating" in review_obj
                assert "comment" in review_obj
                assert "username" in review_obj
        finally:
            # Cleanup
            await review.delete()
    
    @pytest.mark.asyncio
    async def test_pub_011_get_reviews_nonexistent_restaurant(self, async_client):
        """
        TEST ID: PUB-011
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify review retrieval for a non-existent restaurant
        INPUT:
            Method: GET
            URL: /restaurants/NonExistentCafe/reviews
        EXPECTED OUTPUT:
            Status Code: 404 Not Found
            Response Body: Error detail
            Business Rule Validated: Proper 404 handling for reviews
        """
        response = await async_client.get("/restaurants/NonExistentCafe/reviews")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_pub_012_review_pagination_limit(self, async_client, test_restaurant, test_user):
        """
        TEST ID: PUB-012
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify review pagination (limit)
        INPUT:
            Method: GET
            URL: /restaurants/{restaurant_name}/reviews?limit=2
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON array with maximum 2 reviews
            Business Rule Validated: Pagination limit parameter
        """
        # Create 3 test reviews
        reviews = []
        for i in range(3):
            review = Review(
                user_id=test_user.id,
                username=test_user.username,
                restaurant_name=test_restaurant.name,
                rating=5,
                comment=f"Test review number {i+1} with sufficient length for validation."
            )
            await review.insert()
            reviews.append(review)
        
        try:
            response = await async_client.get(
                f"/restaurants/{test_restaurant.name}/reviews?limit=2"
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            assert len(data) <= 2, "Should return maximum 2 reviews"
        finally:
            # Cleanup
            for review in reviews:
                await review.delete()
    
    @pytest.mark.asyncio
    async def test_pub_013_review_pagination_skip(self, async_client, test_restaurant, test_user):
        """
        TEST ID: PUB-013
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify review pagination (skip)
        INPUT:
            Method: GET
            URL: /restaurants/{restaurant_name}/reviews?limit=1&skip=1
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON array with the second review
            Business Rule Validated: Pagination skip parameter
        """
        # Create 2 test reviews
        reviews = []
        for i in range(2):
            review = Review(
                user_id=test_user.id,
                username=f"{test_user.username}_{i}",
                restaurant_name=test_restaurant.name,
                rating=5,
                comment=f"Test review number {i+1} with sufficient length for validation."
            )
            await review.insert()
            reviews.append(review)
        
        try:
            response = await async_client.get(
                f"/restaurants/{test_restaurant.name}/reviews?limit=1&skip=1"
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            assert len(data) == 1, "Should return exactly 1 review"
        finally:
            # Cleanup
            for review in reviews:
                await review.delete()
    
    @pytest.mark.asyncio
    async def test_pub_014_review_statistics(self, async_client, test_restaurant, test_user):
        """
        TEST ID: PUB-014
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify retrieval of review statistics
        INPUT:
            Method: GET
            URL: /restaurants/{restaurant_name}/reviews/stats
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON with total_reviews, average_rating, rating_distribution
            Business Rule Validated: Review statistics calculation
        """
        # Create test reviews with different ratings
        reviews = []
        ratings = [5, 4, 5, 3, 4]
        for i, rating in enumerate(ratings):
            review = Review(
                user_id=test_user.id,
                username=f"{test_user.username}_{i}",
                restaurant_name=test_restaurant.name,
                rating=rating,
                comment=f"Test review with rating {rating} and sufficient length."
            )
            await review.insert()
            reviews.append(review)
        
        try:
            response = await async_client.get(
                f"/restaurants/{test_restaurant.name}/reviews/stats"
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "total_reviews" in data
            assert "average_rating" in data
            assert "rating_distribution" in data
            
            # Validate structure
            assert data["total_reviews"] >= len(ratings)
            assert 1 <= data["average_rating"] <= 5
            
            distribution = data["rating_distribution"]
            for i in range(1, 6):
                assert str(i) in distribution or i in distribution
        finally:
            # Cleanup
            for review in reviews:
                await review.delete()
    
    @pytest.mark.asyncio
    async def test_pub_015_health_check(self, async_client):
        """
        TEST ID: PUB-015
        CATEGORY: Public Endpoints
        DESCRIPTION: Verify the health check endpoint is working
        INPUT:
            Method: GET
            URL: /health
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON with "healthy" status and "connected" database
            Business Rule Validated: System health monitoring
        """
        response = await async_client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert data["version"] == "4.0.0"
        assert "database" in data
        assert "connected" in str(data["database"]).lower()


@pytest.mark.smoke
class TestPublicEndpointsSmokeTests:
    """Quick smoke tests for critical public endpoints"""
    
    @pytest.mark.asyncio
    async def test_api_is_running(self, async_client):
        """Verify API is running and responding"""
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
            ], f"Endpoint {endpoint} should be accessible"
