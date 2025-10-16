"""
Comprehensive Integration Tests for Review System (REV-001 to REV-011)
Aligned with TEST_PLAN_V2.txt - FoodieExpress v4.0.0

TEST COVERAGE:
- REV-001: Valid review submission
- REV-002: Rating out of range (6)
- REV-003: Comment too short
- REV-004: Duplicate review
- REV-005: Restaurant name mismatch
- REV-006: XSS protection in comments
- REV-007: Update own review
- REV-008: Update another user's review (IDOR)
- REV-009: Delete own review
- REV-010: Delete another user's review (IDOR)
- REV-011: Get user's own reviews
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from app.models import Restaurant, User, Review
from app.security import hash_password


@pytest.mark.integration
class TestReviewCreation:
    """Comprehensive test suite for review creation (REV-001 to REV-006)"""
    
    @pytest.mark.asyncio
    async def test_rev_001_create_valid_review(self, async_client, test_user, test_restaurant):
        """
        TEST ID: REV-001
        CATEGORY: Review System
        DESCRIPTION: Test successful submission of a valid review
        INPUT:
            Method: POST
            URL: /restaurants/{restaurant_name}/reviews
            Headers: Authorization: Bearer <token>
            Payload: {"restaurant_name": "Test Restaurant", "rating": 5, "comment": "Excellent food"}
        EXPECTED OUTPUT:
            Status Code: 201 Created
            Response Body: New review object with all fields
            Business Rule Validated: Review submission functionality
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
        
        # Create review
        review_data = {
            "restaurant_name": test_restaurant.name,
            "rating": 5,
            "comment": "Excellent food! Great service and amazing atmosphere."
        }
        
        response = await async_client.post(
            f"/restaurants/{test_restaurant.name}/reviews",
            json=review_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == review_data["comment"]
        assert data["restaurant_name"] == test_restaurant.name
        assert data["username"] == test_user.username
        assert "id" in data
        assert "review_date" in data
        
        # Cleanup
        from beanie import PydanticObjectId
        review = await Review.get(PydanticObjectId(data["id"]))
        if review:
            await review.delete()
    
    @pytest.mark.asyncio
    async def test_rev_002_rating_out_of_range(self, async_client, test_user, test_restaurant):
        """
        TEST ID: REV-002
        CATEGORY: Review System
        DESCRIPTION: Test submitting a review with a rating of 6 (Rule 4.11)
        INPUT:
            Method: POST
            URL: /restaurants/{restaurant_name}/reviews
            Headers: Authorization: Bearer <token>
            Payload: {"restaurant_name": "Test", "rating": 6, "comment": "Good food"}
        EXPECTED OUTPUT:
            Status Code: 422 Unprocessable Entity
            Response Body: Validation error
            Business Rule Validated: Rating must be between 1-5
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
        
        # Try to create review with invalid rating
        review_data = {
            "restaurant_name": test_restaurant.name,
            "rating": 6,  # Invalid: out of range
            "comment": "Good food but rating is invalid for testing purposes."
        }
        
        response = await async_client.post(
            f"/restaurants/{test_restaurant.name}/reviews",
            json=review_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_rev_003_comment_too_short(self, async_client, test_user, test_restaurant):
        """
        TEST ID: REV-003
        CATEGORY: Review System
        DESCRIPTION: Test submitting a review with a comment that is too short (Rule 4.12)
        INPUT:
            Method: POST
            URL: /restaurants/{restaurant_name}/reviews
            Headers: Authorization: Bearer <token>
            Payload: {"restaurant_name": "Test", "rating": 5, "comment": "good"}
        EXPECTED OUTPUT:
            Status Code: 422 Unprocessable Entity
            Response Body: Validation error
            Business Rule Validated: Comment must be at least 10 characters
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
        
        # Try to create review with short comment
        review_data = {
            "restaurant_name": test_restaurant.name,
            "rating": 5,
            "comment": "good"  # Too short: only 4 characters
        }
        
        response = await async_client.post(
            f"/restaurants/{test_restaurant.name}/reviews",
            json=review_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_rev_004_duplicate_review(self, async_client, test_user, test_restaurant):
        """
        TEST ID: REV-004
        CATEGORY: Review System
        DESCRIPTION: Test submitting a duplicate review for the same restaurant (Rule 4.8)
        INPUT:
            Method: POST (twice)
            URL: /restaurants/{restaurant_name}/reviews
            Headers: Authorization: Bearer <token>
            Payload: Same restaurant review
        EXPECTED OUTPUT:
            Status Code: First request = 201, Second request = 400 Bad Request
            Response Body: "You have already reviewed this restaurant"
            Business Rule Validated: One review per user per restaurant
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
        
        # Create first review
        review_data = {
            "restaurant_name": test_restaurant.name,
            "rating": 5,
            "comment": "First review with sufficient length for validation."
        }
        
        first_response = await async_client.post(
            f"/restaurants/{test_restaurant.name}/reviews",
            json=review_data,
            headers=headers
        )
        
        assert first_response.status_code == status.HTTP_201_CREATED
        first_review_id = first_response.json()["id"]
        
        try:
            # Try to create second review for same restaurant
            review_data["comment"] = "Second review attempt with different comment text."
            second_response = await async_client.post(
                f"/restaurants/{test_restaurant.name}/reviews",
                json=review_data,
                headers=headers
            )
            
            assert second_response.status_code == status.HTTP_400_BAD_REQUEST
            data = second_response.json()
            assert "already reviewed" in data["detail"].lower()
        finally:
            # Cleanup
            from beanie import PydanticObjectId
            review = await Review.get(PydanticObjectId(first_review_id))
            if review:
                await review.delete()
    
    @pytest.mark.asyncio
    async def test_rev_005_restaurant_name_mismatch(self, async_client, test_user, test_restaurant):
        """
        TEST ID: REV-005
        CATEGORY: Review System
        DESCRIPTION: Test submitting a review with a name mismatch (Rule 4.14)
        INPUT:
            Method: POST
            URL: /restaurants/RestaurantA/reviews
            Headers: Authorization: Bearer <token>
            Payload: {"restaurant_name": "RestaurantB", "rating": 5, "comment": "..."}
        EXPECTED OUTPUT:
            Status Code: 400 Bad Request
            Response Body: Error about name mismatch
            Business Rule Validated: URL and body restaurant names must match
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
        
        # Create review with mismatched restaurant name
        review_data = {
            "restaurant_name": "Different Restaurant Name",
            "rating": 5,
            "comment": "This review has a mismatched restaurant name for testing."
        }
        
        response = await async_client.post(
            f"/restaurants/{test_restaurant.name}/reviews",
            json=review_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "match" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_rev_006_xss_protection(self, async_client, test_user, test_restaurant):
        """
        TEST ID: REV-006
        CATEGORY: Review System
        DESCRIPTION: Test XSS protection in review comments (Rule 4.13)
        INPUT:
            Method: POST
            URL: /restaurants/{restaurant_name}/reviews
            Headers: Authorization: Bearer <token>
            Payload: {"comment": "<script>alert('XSS')</script>bad food", "rating": 3}
        EXPECTED OUTPUT:
            Status Code: 201 Created
            Response Body: Review with sanitized comment (script tags removed)
            Business Rule Validated: XSS attack prevention
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
        
        # Create review with XSS attempt
        review_data = {
            "restaurant_name": test_restaurant.name,
            "rating": 3,
            "comment": "<script>alert('XSS')</script>The food was mediocre and service slow."
        }
        
        response = await async_client.post(
            f"/restaurants/{test_restaurant.name}/reviews",
            json=review_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify script tag is removed (sanitized)
        assert "<script>" not in data["comment"].lower()
        assert "alert" not in data["comment"].lower()
        # The actual comment text should still be there
        assert "food" in data["comment"].lower() or "mediocre" in data["comment"].lower()
        
        # Cleanup
        from beanie import PydanticObjectId
        review = await Review.get(PydanticObjectId(data["id"]))
        if review:
            await review.delete()


@pytest.mark.integration
class TestReviewUpdateDelete:
    """Comprehensive test suite for review update/delete (REV-007 to REV-010)"""
    
    @pytest.mark.asyncio
    async def test_rev_007_update_own_review(self, async_client, test_user, test_restaurant):
        """
        TEST ID: REV-007
        CATEGORY: Review System
        DESCRIPTION: Test successful update of an owned review
        INPUT:
            Method: PUT
            URL: /reviews/{review_id}
            Headers: Authorization: Bearer <token>
            Payload: {"rating": 4, "comment": "Updated comment"}
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: Updated review object
            Business Rule Validated: User can update their own review
        """
        # Create initial review
        review = Review(
            user_id=test_user.id,
            username=test_user.username,
            restaurant_name=test_restaurant.name,
            rating=3,
            comment="Initial review comment with sufficient length for validation."
        )
        await review.insert()
        
        try:
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
            
            # Update review
            update_data = {
                "rating": 4,
                "comment": "Updated review comment with better feedback and details."
            }
            
            response = await async_client.put(
                f"/reviews/{str(review.id)}",
                json=update_data,
                headers=headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["rating"] == 4
            assert data["comment"] == update_data["comment"]
            assert data["id"] == str(review.id)
        finally:
            # Cleanup
            await review.delete()
    
    @pytest.mark.asyncio
    async def test_rev_008_update_another_users_review_idor(self, async_client, test_restaurant):
        """
        TEST ID: REV-008
        CATEGORY: Review System
        DESCRIPTION: Test failure when updating another user's review (Rule 4.35 / IDOR)
        INPUT:
            Method: PUT
            URL: /reviews/{review_id} (review by User B)
            Headers: Authorization: Bearer <User A token>
            Payload: {"rating": 5, "comment": "Hacked comment"}
        EXPECTED OUTPUT:
            Status Code: 403 Forbidden
            Response Body: "You can only update your own reviews"
            Business Rule Validated: IDOR protection for review updates
        """
        # Create User A
        user_a = User(
            username="user_a_review",
            email="usera_review@example.com",
            hashed_password=hash_password("testpass123"),
            role="user"
        )
        await user_a.insert()
        
        # Create User B
        user_b = User(
            username="user_b_review",
            email="userb_review@example.com",
            hashed_password=hash_password("testpass123"),
            role="user"
        )
        await user_b.insert()
        
        try:
            # Create review by User B
            review_b = Review(
                user_id=user_b.id,
                username=user_b.username,
                restaurant_name=test_restaurant.name,
                rating=4,
                comment="User B's original review with sufficient length."
            )
            await review_b.insert()
            
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
            
            # Try to update User B's review as User A
            update_data = {
                "rating": 1,
                "comment": "Attempting to hack this review with malicious content."
            }
            
            response = await async_client.put(
                f"/reviews/{str(review_b.id)}",
                json=update_data,
                headers=headers_a
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
            data = response.json()
            assert "own reviews" in data["detail"].lower() or \
                   "forbidden" in data["detail"].lower()
            
            # Cleanup review
            await review_b.delete()
        finally:
            # Cleanup users
            await user_a.delete()
            await user_b.delete()
    
    @pytest.mark.asyncio
    async def test_rev_009_delete_own_review(self, async_client, test_user, test_restaurant):
        """
        TEST ID: REV-009
        CATEGORY: Review System
        DESCRIPTION: Test successful deletion of an owned review
        INPUT:
            Method: DELETE
            URL: /reviews/{review_id}
            Headers: Authorization: Bearer <token>
        EXPECTED OUTPUT:
            Status Code: 204 No Content
            Response Body: Empty
            Business Rule Validated: User can delete their own review
        """
        # Create initial review
        review = Review(
            user_id=test_user.id,
            username=test_user.username,
            restaurant_name=test_restaurant.name,
            rating=5,
            comment="Review to be deleted with sufficient length for validation."
        )
        await review.insert()
        
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
        
        # Delete review
        response = await async_client.delete(
            f"/reviews/{str(review.id)}",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify review is deleted
        from beanie import PydanticObjectId
        deleted_review = await Review.get(PydanticObjectId(review.id))
        assert deleted_review is None
    
    @pytest.mark.asyncio
    async def test_rev_010_delete_another_users_review_idor(self, async_client, test_restaurant):
        """
        TEST ID: REV-010
        CATEGORY: Review System
        DESCRIPTION: Test failure when deleting another user's review (Rule 4.35 / IDOR)
        INPUT:
            Method: DELETE
            URL: /reviews/{review_id} (review by User B)
            Headers: Authorization: Bearer <User A token>
        EXPECTED OUTPUT:
            Status Code: 403 Forbidden
            Response Body: "You can only delete your own reviews"
            Business Rule Validated: IDOR protection for review deletion
        """
        # Create User A
        user_a = User(
            username="user_a_delete",
            email="usera_delete@example.com",
            hashed_password=hash_password("testpass123"),
            role="user"
        )
        await user_a.insert()
        
        # Create User B
        user_b = User(
            username="user_b_delete",
            email="userb_delete@example.com",
            hashed_password=hash_password("testpass123"),
            role="user"
        )
        await user_b.insert()
        
        try:
            # Create review by User B
            review_b = Review(
                user_id=user_b.id,
                username=user_b.username,
                restaurant_name=test_restaurant.name,
                rating=5,
                comment="User B's review that should not be deletable by others."
            )
            await review_b.insert()
            
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
            
            # Try to delete User B's review as User A
            response = await async_client.delete(
                f"/reviews/{str(review_b.id)}",
                headers=headers_a
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
            data = response.json()
            assert "own reviews" in data["detail"].lower() or \
                   "forbidden" in data["detail"].lower()
            
            # Verify review still exists
            from beanie import PydanticObjectId
            existing_review = await Review.get(PydanticObjectId(review_b.id))
            assert existing_review is not None
            
            # Cleanup review
            await review_b.delete()
        finally:
            # Cleanup users
            await user_a.delete()
            await user_b.delete()


@pytest.mark.integration
class TestReviewRetrieval:
    """Comprehensive test suite for review retrieval (REV-011)"""
    
    @pytest.mark.asyncio
    async def test_rev_011_get_my_reviews(self, async_client, test_user, test_restaurant):
        """
        TEST ID: REV-011
        CATEGORY: Review System
        DESCRIPTION: Test successful retrieval of the user's own reviews
        INPUT:
            Method: GET
            URL: /users/me/reviews
            Headers: Authorization: Bearer <token>
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON array of reviews created by the current user
            Business Rule Validated: User can view all their reviews
        """
        # Create multiple reviews for test user
        reviews = []
        for i in range(3):
            review = Review(
                user_id=test_user.id,
                username=test_user.username,
                restaurant_name=f"{test_restaurant.name}_{i}",
                rating=4 + (i % 2),
                comment=f"Review number {i+1} with sufficient length for validation purposes."
            )
            await review.insert()
            reviews.append(review)
        
        try:
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
            
            # Get user's reviews
            response = await async_client.get("/users/me/reviews", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            
            # Should contain our test reviews
            review_ids = [str(r["id"]) for r in data]
            for review in reviews:
                assert str(review.id) in review_ids
        finally:
            # Cleanup
            for review in reviews:
                await review.delete()
