"""
FoodieExpress Agent - API Client
=================================
Centralized FastAPI backend connector with retry logic and error handling

This module provides a clean interface for communicating with the FastAPI
backend, including automatic retries, exponential backoff, and proper error handling.

Version: 4.0
Author: Meet Ghadiya
Date: October 2025
"""

import requests
import time
from typing import Dict, Any, Optional, List
from config import config


class APIClient:
    """
    Client for communicating with the FastAPI backend.
    
    Features:
    - Automatic retry with exponential backoff
    - Proper timeout handling
    - Connection pooling
    - Detailed error messages
    - Request/response logging
    """
    
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        """
        Initialize API client.
        
        Args:
            base_url: Backend API base URL (defaults to config)
            timeout: Request timeout in seconds (defaults to config)
        """
        self.base_url = base_url or config.FASTAPI_BASE_URL
        self.timeout = timeout or config.BACKEND_TIMEOUT
        self.max_retries = config.BACKEND_MAX_RETRIES
        
        # Create a session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": f"FoodieAgent/{config.AGENT_VERSION}"
        })
        
        print(f"🔗 API Client initialized: {self.base_url}")
    
    def _retry_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Execute HTTP request with retry logic and exponential backoff.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to request
            **kwargs: Additional arguments for requests
            
        Returns:
            requests.Response object
            
        Raises:
            requests.RequestException: If all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # Log successful request
                print(f"✅ API {method} {url}: {response.status_code}")
                return response
                
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    print(f"❌ API request timed out after {self.max_retries} attempts")
                    raise
                
                backoff = 2 ** attempt
                print(f"⏱️  Timeout (attempt {attempt + 1}/{self.max_retries}), retrying in {backoff}s...")
                time.sleep(backoff)
                
            except requests.exceptions.ConnectionError:
                if attempt == self.max_retries - 1:
                    print(f"❌ API connection failed after {self.max_retries} attempts")
                    raise
                
                backoff = 2 ** attempt
                print(f"🔌 Connection error (attempt {attempt + 1}/{self.max_retries}), retrying in {backoff}s...")
                time.sleep(backoff)
                
            except Exception as e:
                print(f"❌ Unexpected error during API request: {e}")
                raise
        
        raise requests.RequestException("Max retries exceeded")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make API request and return JSON response.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (relative to base_url)
            **kwargs: Additional arguments
            
        Returns:
            dict: JSON response or error dict
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self._retry_request(method, url, **kwargs)
            
            # Handle different status codes
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 404:
                return {"error": "Not found", "status_code": 404}
            elif response.status_code == 401:
                return {"error": "Unauthorized", "status_code": 401}
            elif response.status_code == 422:
                return {"error": "Validation error", "detail": response.json().get("detail"), "status_code": 422}
            else:
                return {"error": f"HTTP {response.status_code}", "status_code": response.status_code}
                
        except requests.exceptions.Timeout:
            return {"error": "Request timed out", "status_code": 408}
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot connect to backend", "status_code": 503}
        except Exception as e:
            return {"error": str(e), "status_code": 500}
    
    # ==================== RESTAURANT ENDPOINTS ====================
    
    def get_all_restaurants(self) -> List[Dict[str, Any]]:
        """Get all restaurants"""
        result = self._make_request("GET", "/restaurants/")
        if isinstance(result, list):
            return result
        return []
    
    def get_restaurant_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get specific restaurant by name"""
        result = self._make_request("GET", f"/restaurants/{name}")
        if "error" in result:
            return None
        return result
    
    def search_restaurants_by_cuisine(self, cuisine: str) -> List[Dict[str, Any]]:
        """Search restaurants by cuisine"""
        result = self._make_request("GET", "/restaurants/", params={"cuisine": cuisine})
        if isinstance(result, list):
            return result
        return []
    
    def search_restaurants_by_item(self, item_name: str) -> List[Dict[str, Any]]:
        """Search restaurants that serve a specific item"""
        result = self._make_request("GET", "/search/items", params={"item_name": item_name})
        if isinstance(result, list):
            return result
        return []
    
    # ==================== ORDER ENDPOINTS ====================
    
    def place_order(self, restaurant_name: str, items: List[Dict[str, Any]], token: str) -> Dict[str, Any]:
        """
        Place an order.
        
        Args:
            restaurant_name: Name of restaurant
            items: List of items with item_name, quantity, price
            token: Authentication token
            
        Returns:
            dict: Order details or error
        """
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "restaurant_name": restaurant_name,
            "items": items
        }
        return self._make_request("POST", "/orders/", json=data, headers=headers)
    
    def get_user_orders(self, token: str) -> List[Dict[str, Any]]:
        """Get all orders for authenticated user"""
        headers = {"Authorization": f"Bearer {token}"}
        result = self._make_request("GET", "/orders/", headers=headers)
        if isinstance(result, list):
            return result
        return []
    
    # ==================== REVIEW ENDPOINTS ====================
    
    def add_review(self, restaurant_name: str, rating: int, comment: str, token: str) -> Dict[str, Any]:
        """Submit a review"""
        headers = {"Authorization": f"Bearer {token}"}
        data = {"rating": rating, "comment": comment}
        return self._make_request("POST", f"/restaurants/{restaurant_name}/reviews", json=data, headers=headers)
    
    def get_reviews(self, restaurant_name: str) -> List[Dict[str, Any]]:
        """Get all reviews for a restaurant"""
        result = self._make_request("GET", f"/restaurants/{restaurant_name}/reviews")
        if isinstance(result, list):
            return result
        return []
    
    def get_review_stats(self, restaurant_name: str) -> Dict[str, Any]:
        """Get review statistics"""
        return self._make_request("GET", f"/restaurants/{restaurant_name}/reviews/stats")
    
    def get_my_reviews(self, token: str) -> List[Dict[str, Any]]:
        """Get reviews written by current user"""
        headers = {"Authorization": f"Bearer {token}"}
        result = self._make_request("GET", "/users/me/reviews", headers=headers)
        if isinstance(result, list):
            return result
        return []
    
    # ==================== USER/AUTH ENDPOINTS ====================
    
    def register_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        data = {"username": username, "email": email, "password": password}
        return self._make_request("POST", "/users/register", json=data)
    
    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """Login user and get token"""
        data = {"username": username, "password": password}
        return self._make_request("POST", "/users/login", data=data)
    
    def get_user_info(self, token: str) -> Dict[str, Any]:
        """Get current user information"""
        headers = {"Authorization": f"Bearer {token}"}
        return self._make_request("GET", "/users/me", headers=headers)
    
    # ==================== HEALTH CHECK ====================
    
    def health_check(self) -> Dict[str, Any]:
        """Check backend health"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            return {
                "status": "healthy",
                "status_code": response.status_code,
                "backend": self.base_url
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "backend": self.base_url
            }


# Create a singleton instance
api_client = APIClient()


if __name__ == "__main__":
    # Test the API client
    print("\n🧪 Testing API Client...")
    print("=" * 60)
    
    # Health check
    print("\n📊 Health Check:")
    health = api_client.health_check()
    for k, v in health.items():
        print(f"  • {k}: {v}")
    
    # Test get all restaurants
    print("\n🧪 Test 1: Get all restaurants")
    restaurants = api_client.get_all_restaurants()
    print(f"  Found {len(restaurants)} restaurants")
    if restaurants:
        print(f"  First restaurant: {restaurants[0].get('name')}")
    
    # Test search by cuisine
    print("\n🧪 Test 2: Search by cuisine (Gujarati)")
    gujarati = api_client.search_restaurants_by_cuisine("Gujarati")
    print(f"  Found {len(gujarati)} Gujarati restaurants")
    
    # Test search by item
    print("\n🧪 Test 3: Search by item (Pizza)")
    pizza_places = api_client.search_restaurants_by_item("Pizza")
    print(f"  Found {len(pizza_places)} places serving Pizza")
    
    # Test get specific restaurant
    print("\n🧪 Test 4: Get specific restaurant (Swati Snacks)")
    restaurant = api_client.get_restaurant_by_name("Swati Snacks")
    if restaurant:
        print(f"  Restaurant: {restaurant.get('name')}")
        print(f"  Area: {restaurant.get('area')}")
        print(f"  Cuisine: {restaurant.get('cuisine')}")
    else:
        print("  Restaurant not found")
    
    print("\n" + "=" * 60)
    print("✅ API Client tests complete!")
