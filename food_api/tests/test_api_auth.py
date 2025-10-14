"""
Integration Tests for Authentication Endpoints
Tests user registration, login, and protected endpoint access

TEST COVERAGE:
- User registration validation
- Login authentication flow
- JWT token generation
- Protected endpoint authorization
- Error handling and edge cases
"""

import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.integration
class TestUserRegistration:
    """Test user registration endpoint"""
    
    @pytest.mark.asyncio
    async def test_register_new_user_success(self, async_client):
        """Test successful user registration"""
        user_data = {
            "username": "newuser456",
            "email": "newuser456@example.com",
            "password": "SecurePass123"
        }
        
        response = await async_client.post("/users/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "password" not in data  # Password should never be returned
        assert "hashed_password" not in data
        assert data["role"] == "user"  # Default role
    
    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, async_client, test_user):
        """Test that registering duplicate username fails"""
        duplicate_user = {
            "username": test_user.username,  # Already exists from fixture
            "email": "different@example.com",
            "password": "AnotherPass123"
        }
        
        response = await async_client.post("/users/register", json=duplicate_user)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username already exists" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client, test_user):
        """Test that registering duplicate email fails"""
        duplicate_user = {
            "username": "differentuser",
            "email": test_user.email,  # Already exists from fixture
            "password": "AnotherPass123"
        }
        
        response = await async_client.post("/users/register", json=duplicate_user)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email already exists" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, async_client):
        """Test that weak passwords are rejected by validation"""
        weak_password_user = {
            "username": "testuser789",
            "email": "test789@example.com",
            "password": "weak"  # Too short, no numbers
        }
        
        response = await async_client.post("/users/register", json=weak_password_user)
        
        # Should be rejected by Pydantic validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client):
        """Test that invalid email format is rejected"""
        invalid_email_user = {
            "username": "testuser999",
            "email": "not-an-email",  # Invalid format
            "password": "SecurePass123"
        }
        
        response = await async_client.post("/users/register", json=invalid_email_user)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
class TestUserLogin:
    """Test user login and authentication"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, async_client, test_user):
        """Test successful login with correct credentials"""
        response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"  # Plain text password from fixture
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client, test_user):
        """Test login fails with incorrect password"""
        response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect username or password" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client):
        """Test login fails for non-existent user"""
        response = await async_client.post(
            "/users/login",
            data={
                "username": "nonexistentuser",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_login_rate_limiting(self, async_client, test_user):
        """
        Test that login endpoint is rate-limited (5 attempts per minute)
        HIGH-002 Security Fix Validation
        """
        # Make 6 rapid login attempts (rate limit is 5/minute)
        responses = []
        for _ in range(6):
            response = await async_client.post(
                "/users/login",
                data={
                    "username": test_user.username,
                    "password": "wrongpassword"
                }
            )
            responses.append(response)
        
        # At least one should be rate limited (429 Too Many Requests)
        status_codes = [r.status_code for r in responses]
        
        # First 5 should be 401 Unauthorized, 6th should be 429 Too Many Requests
        assert status.HTTP_429_TOO_MANY_REQUESTS in status_codes


@pytest.mark.integration
class TestProtectedEndpoints:
    """Test authentication requirements for protected endpoints"""
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_no_token(self, async_client):
        """Test that protected endpoint requires authentication"""
        # Try to create an order without authentication
        order_data = {
            "restaurant_name": "Test Restaurant",
            "items": [
                {"item_name": "Test Item", "quantity": 1, "price": 100}
            ]
        }
        
        response = await async_client.post("/orders/", json=order_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "not authenticated" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_invalid_token(self, async_client):
        """Test that invalid tokens are rejected"""
        order_data = {
            "restaurant_name": "Test Restaurant",
            "items": [
                {"item_name": "Test Item", "quantity": 1, "price": 100}
            ]
        }
        
        # Use an invalid token
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await async_client.post("/orders/", json=order_data, headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_with_valid_token(self, async_client, auth_token, test_restaurant):
        """Test that valid tokens grant access to protected endpoints"""
        order_data = {
            "restaurant_name": test_restaurant.name,
            "items": [
                {"item_name": "Test Item", "quantity": 1, "price": 100}
            ]
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = await async_client.post("/orders/", json=order_data, headers=headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["restaurant_name"] == test_restaurant.name
    
    @pytest.mark.asyncio
    async def test_get_current_user_info(self, async_client, auth_token, test_user):
        """Test getting current user information with valid token"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = await async_client.get("/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert "password" not in data
        assert "hashed_password" not in data


@pytest.mark.security
class TestAuthenticationSecurity:
    """Security-focused authentication tests"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_login(self, async_client):
        """Test that SQL injection attempts in login are handled safely"""
        malicious_inputs = [
            "admin' OR '1'='1",
            "'; DROP TABLE users; --",
            "admin'--",
        ]
        
        for malicious_input in malicious_inputs:
            response = await async_client.post(
                "/users/login",
                data={
                    "username": malicious_input,
                    "password": "anypassword"
                }
            )
            
            # Should return 401, not crash or succeed
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_password_not_returned_in_responses(self, async_client):
        """Test that passwords are never included in API responses"""
        user_data = {
            "username": "securitytest123",
            "email": "sectest@example.com",
            "password": "SecurePass123"
        }
        
        # Register user
        register_response = await async_client.post("/users/register", json=user_data)
        assert "password" not in register_response.text
        assert "hashed_password" not in register_response.text
        
        # Login
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": user_data["username"],
                "password": user_data["password"]
            }
        )
        assert "password" not in login_response.text
        assert "hashed_password" not in login_response.text
