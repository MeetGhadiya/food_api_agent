"""
Test Suite for api_client.py - Backend API Client
Tests API calls, retry logic, error handling, and timeout management
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api_client import APIClient


class TestAPIClientInitialization:
    """Test API client initialization"""
    
    def test_initialization_with_defaults(self):
        """Test initialization with default parameters"""
        client = APIClient()
        
        assert client.base_url == "http://localhost:8000"
        assert client.timeout == 10
        assert client.max_retries == 3
        assert client.session is not None
    
    def test_initialization_with_custom_params(self):
        """Test initialization with custom parameters"""
        client = APIClient(
            base_url="http://api.example.com",
            timeout=30,
            max_retries=5
        )
        
        assert client.base_url == "http://api.example.com"
        assert client.timeout == 30
        assert client.max_retries == 5


class TestAPIClientRestaurantEndpoints:
    """Test restaurant-related API calls"""
    
    @patch('requests.Session.request')
    def test_get_all_restaurants_success(self, mock_request):
        """Test successful get all restaurants"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "1", "name": "Pizza Place"},
            {"id": "2", "name": "Burger Joint"}
        ]
        mock_request.return_value = mock_response
        
        client = APIClient()
        result = client.get_all_restaurants()
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "Pizza Place"
    
    @patch('requests.Session.request')
    def test_get_restaurant_by_id(self, mock_request):
        """Test get restaurant by ID"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "1", "name": "Pizza Place"}
        mock_request.return_value = mock_response
        
        client = APIClient()
        result = client.get_restaurant_by_id("1")
        
        assert result["id"] == "1"
        assert result["name"] == "Pizza Place"
    
    @patch('requests.Session.request')
    def test_search_restaurants(self, mock_request):
        """Test search restaurants"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "1", "name": "Pizza Place"}]
        mock_request.return_value = mock_response
        
        client = APIClient()
        result = client.search_restaurants(name="Pizza")
        
        assert isinstance(result, list)
        assert len(result) == 1


class TestAPIClientAuthenticationEndpoints:
    """Test authentication-related API calls"""
    
    @patch('requests.Session.request')
    def test_register_user(self, mock_request):
        """Test user registration"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "email": "test@example.com",
            "message": "User created"
        }
        mock_request.return_value = mock_response
        
        client = APIClient()
        result = client.register_user("test@example.com", "password123")
        
        assert result["email"] == "test@example.com"
        assert "message" in result
    
    @patch('requests.Session.request')
    def test_login_user(self, mock_request):
        """Test user login"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "fake_token_123",
            "token_type": "bearer"
        }
        mock_request.return_value = mock_response
        
        client = APIClient()
        result = client.login_user("test@example.com", "password123")
        
        assert "access_token" in result
        assert result["token_type"] == "bearer"


class TestAPIClientOrderEndpoints:
    """Test order-related API calls"""
    
    @patch('requests.Session.request')
    def test_create_order(self, mock_request):
        """Test create order"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "order_id": "order_123",
            "status": "pending"
        }
        mock_request.return_value = mock_response
        
        client = APIClient()
        order_data = {
            "restaurant_id": "rest_1",
            "items": ["Pizza", "Coke"]
        }
        result = client.create_order(order_data, "fake_token")
        
        assert result["order_id"] == "order_123"
        assert result["status"] == "pending"
    
    @patch('requests.Session.request')
    def test_get_user_orders(self, mock_request):
        """Test get user orders"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"order_id": "1", "total": 25.99},
            {"order_id": "2", "total": 15.50}
        ]
        mock_request.return_value = mock_response
        
        client = APIClient()
        result = client.get_user_orders("fake_token")
        
        assert isinstance(result, list)
        assert len(result) == 2


class TestAPIClientRetryLogic:
    """Test retry logic for failed requests"""
    
    @patch('requests.Session.request')
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_retry_on_timeout(self, mock_sleep, mock_request):
        """Test retry logic when request times out"""
        # Fail twice with timeout, succeed on third attempt
        mock_request.side_effect = [
            requests.exceptions.Timeout("Request timeout"),
            requests.exceptions.Timeout("Request timeout"),
            Mock(status_code=200, json=lambda: {"success": True})
        ]
        
        client = APIClient()
        result = client.get_all_restaurants()
        
        assert result == {"success": True}
        assert mock_request.call_count == 3
        assert mock_sleep.call_count == 2  # Slept between retries
    
    @patch('requests.Session.request')
    def test_no_retry_on_client_error(self, mock_request):
        """Test no retry on 4xx client errors"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not found"}
        mock_request.return_value = mock_response
        
        client = APIClient()
        result = client.get_restaurant_by_id("nonexistent")
        
        # Should not retry on 404
        assert mock_request.call_count == 1
        assert "error" in result
    
    @patch('requests.Session.request')
    @patch('time.sleep')
    def test_retry_on_server_error(self, mock_sleep, mock_request):
        """Test retry on 5xx server errors"""
        # Fail twice with 500, succeed on third attempt
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.raise_for_status.side_effect = requests.exceptions.HTTPError()
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"success": True}
        
        mock_request.side_effect = [
            mock_response_fail,
            mock_response_fail,
            mock_response_success
        ]
        
        client = APIClient()
        result = client.get_all_restaurants()
        
        assert result == {"success": True}
        assert mock_request.call_count == 3


class TestAPIClientErrorHandling:
    """Test error handling and normalization"""
    
    @patch('requests.Session.request')
    def test_connection_error_handling(self, mock_request):
        """Test handling of connection errors"""
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        client = APIClient()
        result = client.get_all_restaurants()
        
        assert "error" in result
        assert "status_code" in result
        assert result["status_code"] == 503  # Service Unavailable
    
    @patch('requests.Session.request')
    def test_timeout_error_handling(self, mock_request):
        """Test handling of timeout errors"""
        mock_request.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = APIClient()
        result = client.get_all_restaurants()
        
        assert "error" in result
        assert "timeout" in result["error"].lower()
        assert result["status_code"] == 408  # Request Timeout
    
    @patch('requests.Session.request')
    def test_json_decode_error_handling(self, mock_request):
        """Test handling of invalid JSON responses"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_request.return_value = mock_response
        
        client = APIClient()
        result = client.get_all_restaurants()
        
        assert "error" in result
        assert "json" in result["error"].lower()


class TestAPIClientReviewEndpoints:
    """Test review-related API calls"""
    
    @patch('requests.Session.request')
    def test_create_review(self, mock_request):
        """Test create review"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "review_id": "review_123",
            "rating": 5
        }
        mock_request.return_value = mock_response
        
        client = APIClient()
        review_data = {
            "restaurant_id": "rest_1",
            "rating": 5,
            "comment": "Excellent!"
        }
        result = client.create_review(review_data, "fake_token")
        
        assert result["review_id"] == "review_123"
        assert result["rating"] == 5
    
    @patch('requests.Session.request')
    def test_get_restaurant_reviews(self, mock_request):
        """Test get restaurant reviews"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"rating": 5, "comment": "Great!"},
            {"rating": 4, "comment": "Good"}
        ]
        mock_request.return_value = mock_response
        
        client = APIClient()
        result = client.get_restaurant_reviews("rest_1")
        
        assert isinstance(result, list)
        assert len(result) == 2


class TestAPIClientAdminEndpoints:
    """Test admin-related API calls"""
    
    @patch('requests.Session.request')
    def test_get_admin_stats(self, mock_request):
        """Test get admin statistics"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_users": 100,
            "total_orders": 500,
            "total_revenue": 15000.00
        }
        mock_request.return_value = mock_response
        
        client = APIClient()
        result = client.get_admin_stats("admin_token")
        
        assert result["total_users"] == 100
        assert result["total_orders"] == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
