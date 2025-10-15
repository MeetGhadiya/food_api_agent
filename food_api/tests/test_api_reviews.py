"""
V4.0: Test Suite for Review API Endpoints
Tests for review creation, reading, updating, and deleting
"""
import pytest
from fastapi.testclient import TestClient
from beanie import PydanticObjectId
from datetime import datetime

# Tests will use the conftest.py fixtures


def test_create_review_success(client: TestClient, auth_token: str, sample_restaurant):
    """Test successful review creation"""
    review_data = {
        "restaurant_name": sample_restaurant["name"],
        "rating": 5,
        "comment": "Absolutely amazing food! The best I've ever had. Highly recommend to everyone!"
    }
    
    response = client.post(
        f"/restaurants/{sample_restaurant['name']}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["restaurant_name"] == sample_restaurant["name"]
    assert data["rating"] == 5
    assert data["username"] is not None
    assert "Absolutely amazing" in data["comment"]
    assert data["helpful_count"] == 0
    assert "is_verified_purchase" in data


def test_create_review_requires_auth(client: TestClient, sample_restaurant):
    """Test that review creation requires authentication"""
    review_data = {
        "restaurant_name": sample_restaurant["name"],
        "rating": 4,
        "comment": "Great food but no authentication"
    }
    
    response = client.post(
        f"/restaurants/{sample_restaurant['name']}/reviews",
        json=review_data
    )
    
    assert response.status_code == 401


def test_create_review_invalid_rating(client: TestClient, auth_token: str, sample_restaurant):
    """Test that invalid ratings are rejected"""
    # Rating too high
    review_data = {
        "restaurant_name": sample_restaurant["name"],
        "rating": 6,
        "comment": "This should fail validation"
    }
    
    response = client.post(
        f"/restaurants/{sample_restaurant['name']}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 422  # Validation error
    
    # Rating too low
    review_data["rating"] = 0
    response = client.post(
        f"/restaurants/{sample_restaurant['name']}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 422


def test_create_review_comment_too_short(client: TestClient, auth_token: str, sample_restaurant):
    """Test that short comments are rejected"""
    review_data = {
        "restaurant_name": sample_restaurant["name"],
        "rating": 5,
        "comment": "Short"  # Less than 10 characters
    }
    
    response = client.post(
        f"/restaurants/{sample_restaurant['name']}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 422


def test_create_duplicate_review(client: TestClient, auth_token: str, sample_restaurant):
    """Test that duplicate reviews are prevented"""
    review_data = {
        "restaurant_name": sample_restaurant["name"],
        "rating": 5,
        "comment": "First review is great!"
    }
    
    # Create first review
    response1 = client.post(
        f"/restaurants/{sample_restaurant['name']}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response1.status_code == 201
    
    # Try to create duplicate
    response2 = client.post(
        f"/restaurants/{sample_restaurant['name']}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response2.status_code == 400
    assert "already reviewed" in response2.json()["detail"].lower()


def test_get_restaurant_reviews(client: TestClient, auth_token: str, sample_restaurant):
    """Test fetching reviews for a restaurant"""
    # Create a few reviews first (need multiple test users for this)
    review_data = {
        "restaurant_name": sample_restaurant["name"],
        "rating": 4,
        "comment": "Good food, nice ambiance, would visit again!"
    }
    
    client.post(
        f"/restaurants/{sample_restaurant['name']}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Get reviews
    response = client.get(f"/restaurants/{sample_restaurant['name']}/reviews")
    
    assert response.status_code == 200
    reviews = response.json()
    assert isinstance(reviews, list)
    assert len(reviews) >= 1
    assert reviews[0]["restaurant_name"] == sample_restaurant["name"]
    assert "rating" in reviews[0]
    assert "comment" in reviews[0]


def test_get_reviews_with_pagination(client: TestClient, sample_restaurant):
    """Test review pagination"""
    response = client.get(
        f"/restaurants/{sample_restaurant['name']}/reviews",
        params={"limit": 5, "skip": 0}
    )
    
    assert response.status_code == 200
    reviews = response.json()
    assert len(reviews) <= 5


def test_get_reviews_nonexistent_restaurant(client: TestClient):
    """Test getting reviews for non-existent restaurant"""
    response = client.get("/restaurants/NonExistentRestaurant/reviews")
    
    assert response.status_code == 404


def test_update_review(client: TestClient, auth_token: str, sample_restaurant):
    """Test updating an existing review"""
    # Create review
    review_data = {
        "restaurant_name": sample_restaurant["name"],
        "rating": 3,
        "comment": "It was okay, nothing special really."
    }
    
    create_response = client.post(
        f"/restaurants/{sample_restaurant['name']}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert create_response.status_code == 201
    review_id = create_response.json()["id"]
    
    # Update review
    update_data = {
        "rating": 5,
        "comment": "Changed my mind - absolutely fantastic food! Best experience ever!"
    }
    
    update_response = client.put(
        f"/reviews/{review_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert update_response.status_code == 200
    updated_review = update_response.json()
    assert updated_review["rating"] == 5
    assert "fantastic" in updated_review["comment"]


def test_update_review_unauthorized(client: TestClient, auth_token: str, sample_restaurant):
    """Test that users cannot update others' reviews"""
    # This would need a second user to properly test
    # For now, test with invalid review ID
    update_data = {
        "rating": 5,
        "comment": "Trying to update someone else's review"
    }
    
    fake_id = str(PydanticObjectId())
    response = client.put(
        f"/reviews/{fake_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 404


def test_delete_review(client: TestClient, auth_token: str, sample_restaurant):
    """Test deleting a review"""
    # Create review
    review_data = {
        "restaurant_name": sample_restaurant["name"],
        "rating": 2,
        "comment": "Not good, decided to delete this review."
    }
    
    create_response = client.post(
        f"/restaurants/{sample_restaurant['name']}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert create_response.status_code == 201
    review_id = create_response.json()["id"]
    
    # Delete review
    delete_response = client.delete(
        f"/reviews/{review_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert delete_response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/restaurants/{sample_restaurant['name']}/reviews")
    reviews = get_response.json()
    review_ids = [r["id"] for r in reviews]
    assert review_id not in review_ids


def test_get_my_reviews(client: TestClient, auth_token: str, sample_restaurant):
    """Test getting current user's reviews"""
    # Create a review
    review_data = {
        "restaurant_name": sample_restaurant["name"],
        "rating": 4,
        "comment": "This is my review that I should see in my history."
    }
    
    client.post(
        f"/restaurants/{sample_restaurant['name']}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Get my reviews
    response = client.get(
        "/users/me/reviews",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    reviews = response.json()
    assert isinstance(reviews, list)
    assert len(reviews) >= 1
    assert any(r["comment"] == review_data["comment"] for r in reviews)


def test_get_my_reviews_requires_auth(client: TestClient):
    """Test that getting my reviews requires authentication"""
    response = client.get("/users/me/reviews")
    
    assert response.status_code == 401


def test_review_xss_protection(client: TestClient, auth_token: str, sample_restaurant):
    """Test that XSS attempts in comments are sanitized"""
    review_data = {
        "restaurant_name": sample_restaurant["name"],
        "rating": 3,
        "comment": "<script>alert('XSS')</script>Great food but this script should be removed!"
    }
    
    response = client.post(
        f"/restaurants/{sample_restaurant['name']}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    # Script tags should be removed
    assert "<script>" not in data["comment"]
    assert "alert" not in data["comment"]
    assert "Great food" in data["comment"]


def test_review_stats(client: TestClient, auth_token: str, sample_restaurant):
    """Test getting review statistics for a restaurant"""
    # Create multiple reviews with different ratings
    for rating in [5, 4, 5, 3, 5]:
        review_data = {
            "restaurant_name": sample_restaurant["name"],
            "rating": rating,
            "comment": f"Test review with rating {rating} stars for statistics."
        }
        # This would need multiple users, but for basic test:
        try:
            client.post(
                f"/restaurants/{sample_restaurant['name']}/reviews",
                json=review_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )
        except:
            pass  # Skip if duplicate
    
    # Get stats
    response = client.get(f"/restaurants/{sample_restaurant['name']}/reviews/stats")
    
    assert response.status_code == 200
    stats = response.json()
    assert "total_reviews" in stats
    assert "average_rating" in stats
    assert "rating_distribution" in stats
    assert stats["total_reviews"] >= 1
