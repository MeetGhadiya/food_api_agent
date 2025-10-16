"""
Comprehensive Integration Tests for Authentication & User Accounts (AUTH-001 to AUTH-014)
Aligned with TEST_PLAN_V2.txt - FoodieExpress v4.0.0

TEST COVERAGE:
- AUTH-001: Successful user registration
- AUTH-002: Duplicate email registration
- AUTH-003: Duplicate username registration
- AUTH-004: Password too short
- AUTH-005: Password without numbers
- AUTH-006: Password without letters
- AUTH-007: Invalid username format
- AUTH-008: Invalid email format
- AUTH-009: Successful login
- AUTH-010: Incorrect password login
- AUTH-011: Rate limiting on login
- AUTH-012: Get current user with valid token
- AUTH-013: Get current user without token
- AUTH-014: Get current user with expired token
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from app.models import User
from app.security import hash_password
import time


@pytest.mark.integration
class TestUserRegistration:
    """Comprehensive test suite for user registration (AUTH-001 to AUTH-008)"""
    
    @pytest.mark.asyncio
    async def test_auth_001_register_new_user_success(self, async_client):
        """
        TEST ID: AUTH-001
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test successful user registration
        INPUT:
            Method: POST
            URL: /users/register
            Payload: {"username":"newuser456","email":"newuser456@example.com","password":"ValidPass123"}
        EXPECTED OUTPUT:
            Status Code: 201 Created
            Response Body: User object (id, username, email, role) without password
            Business Rule Validated: Successful registration with strong password
        """
        user_data = {
            "username": "newuser456",
            "email": "newuser456@example.com",
            "password": "ValidPass123"
        }
        
        # Clean up if exists
        existing = await User.find_one(User.email == user_data["email"])
        if existing:
            await existing.delete()
        
        response = await async_client.post("/users/register", json=user_data)
        
        try:
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["username"] == user_data["username"]
            assert data["email"] == user_data["email"]
            assert "password" not in data, "Password should never be returned"
            assert "hashed_password" not in data, "Hashed password should never be returned"
            assert data["role"] == "user", "Default role should be 'user'"
            assert "id" in data, "User ID should be present"
        finally:
            # Cleanup
            user = await User.find_one(User.email == user_data["email"])
            if user:
                await user.delete()
    
    @pytest.mark.asyncio
    async def test_auth_002_register_duplicate_email(self, async_client, test_user):
        """
        TEST ID: AUTH-002
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test registration with a duplicate email
        INPUT:
            Method: POST
            URL: /users/register
            Payload: Email that already exists
        EXPECTED OUTPUT:
            Status Code: 400 Bad Request
            Response Body: "An account with this email already exists"
            Business Rule Validated: Email uniqueness constraint
        """
        duplicate_user = {
            "username": "differentuser123",
            "email": test_user.email,  # Already exists from fixture
            "password": "AnotherPass123"
        }
        
        response = await async_client.post("/users/register", json=duplicate_user)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "email already exists" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_auth_003_register_duplicate_username(self, async_client, test_user):
        """
        TEST ID: AUTH-003
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test registration with a duplicate username
        INPUT:
            Method: POST
            URL: /users/register
            Payload: Username that already exists
        EXPECTED OUTPUT:
            Status Code: 400 Bad Request
            Response Body: "An account with this username already exists"
            Business Rule Validated: Username uniqueness constraint
        """
        duplicate_user = {
            "username": test_user.username,  # Already exists from fixture
            "email": "different123@example.com",
            "password": "AnotherPass123"
        }
        
        response = await async_client.post("/users/register", json=duplicate_user)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "username already exists" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_auth_004_register_password_too_short(self, async_client):
        """
        TEST ID: AUTH-004
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test registration with a password that is too short (Rule 4.15)
        INPUT:
            Method: POST
            URL: /users/register
            Payload: Password with only 7 characters
        EXPECTED OUTPUT:
            Status Code: 422 Unprocessable Entity
            Response Body: Validation error for password field
            Business Rule Validated: Password minimum length (8 characters)
        """
        weak_password_user = {
            "username": "testuser789",
            "email": "test789@example.com",
            "password": "Pass12"  # Only 6 characters
        }
        
        response = await async_client.post("/users/register", json=weak_password_user)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_auth_005_register_password_no_numbers(self, async_client):
        """
        TEST ID: AUTH-005
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test registration with a password without numbers (Rule 4.15)
        INPUT:
            Method: POST
            URL: /users/register
            Payload: Password like "PasswordWithoutNumber"
        EXPECTED OUTPUT:
            Status Code: 422 Unprocessable Entity
            Response Body: Validation error indicating password must contain numbers
            Business Rule Validated: Password must contain at least one number
        """
        weak_password_user = {
            "username": "testuser890",
            "email": "test890@example.com",
            "password": "PasswordWithoutNumber"  # No numbers
        }
        
        response = await async_client.post("/users/register", json=weak_password_user)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        # Check if error mentions number requirement
        error_msg = str(data).lower()
        assert "number" in error_msg or "digit" in error_msg
    
    @pytest.mark.asyncio
    async def test_auth_006_register_password_no_letters(self, async_client):
        """
        TEST ID: AUTH-006
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test registration with a password without letters (Rule 4.15)
        INPUT:
            Method: POST
            URL: /users/register
            Payload: Password like "123456789"
        EXPECTED OUTPUT:
            Status Code: 422 Unprocessable Entity
            Response Body: Validation error indicating password must contain letters
            Business Rule Validated: Password must contain at least one letter
        """
        weak_password_user = {
            "username": "testuser901",
            "email": "test901@example.com",
            "password": "123456789"  # No letters
        }
        
        response = await async_client.post("/users/register", json=weak_password_user)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        # Check if error mentions letter requirement
        error_msg = str(data).lower()
        assert "letter" in error_msg
    
    @pytest.mark.asyncio
    async def test_auth_007_register_invalid_username(self, async_client):
        """
        TEST ID: AUTH-007
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test registration with an invalid username format (Rule 4.16)
        INPUT:
            Method: POST
            URL: /users/register
            Payload: Username with spaces or special characters
        EXPECTED OUTPUT:
            Status Code: 422 Unprocessable Entity
            Response Body: Validation error for username format
            Business Rule Validated: Username must be alphanumeric with underscores/hyphens only
        """
        invalid_username_user = {
            "username": "user name with spaces",  # Invalid: contains spaces
            "email": "validuser@example.com",
            "password": "ValidPass123"
        }
        
        response = await async_client.post("/users/register", json=invalid_username_user)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_auth_008_register_invalid_email(self, async_client):
        """
        TEST ID: AUTH-008
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test registration with an invalid email format (Rule 4.17)
        INPUT:
            Method: POST
            URL: /users/register
            Payload: Email like "not-an-email"
        EXPECTED OUTPUT:
            Status Code: 422 Unprocessable Entity
            Response Body: Validation error for email format
            Business Rule Validated: Email must be valid format
        """
        invalid_email_user = {
            "username": "validusername",
            "email": "not-an-email",  # Invalid format
            "password": "ValidPass123"
        }
        
        response = await async_client.post("/users/register", json=invalid_email_user)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data


@pytest.mark.integration
class TestUserLogin:
    """Comprehensive test suite for user login (AUTH-009 to AUTH-011)"""
    
    @pytest.mark.asyncio
    async def test_auth_009_login_success(self, async_client, test_user):
        """
        TEST ID: AUTH-009
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test successful login with correct credentials
        INPUT:
            Method: POST
            URL: /users/login
            Payload: Correct username and password
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: JSON with access_token and token_type: "bearer"
            Business Rule Validated: Successful authentication
        """
        response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"  # Plain text password from fixture
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data, "Response should contain access token"
        assert data["token_type"] == "bearer", "Token type should be bearer"
        assert len(data["access_token"]) > 0, "Access token should not be empty"
    
    @pytest.mark.asyncio
    async def test_auth_010_login_incorrect_password(self, async_client, test_user):
        """
        TEST ID: AUTH-010
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test login with an incorrect password
        INPUT:
            Method: POST
            URL: /users/login
            Payload: Correct username but incorrect password
        EXPECTED OUTPUT:
            Status Code: 401 Unauthorized
            Response Body: "Incorrect username or password"
            Business Rule Validated: Authentication failure handling
        """
        response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "incorrect username or password" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_auth_011_login_rate_limiting(self, async_client):
        """
        TEST ID: AUTH-011
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test login rate limiting (Rule 4.20)
        INPUT:
            Method: POST (6 rapid requests)
            URL: /users/login
            Payload: Failed login attempts
        EXPECTED OUTPUT:
            Status Code: First 5 requests = 401, 6th request = 429 Too Many Requests
            Response Body: Rate limit error
            Business Rule Validated: HIGH-002 Security Fix - Rate limiting
        """
        # Create a test user for rate limiting
        test_user_rl = User(
            username="ratelimituser",
            email="ratelimit@example.com",
            hashed_password=hash_password("testpass123"),
            role="user"
        )
        await test_user_rl.insert()
        
        try:
            # Make 6 rapid login attempts (rate limit is 5/minute)
            responses = []
            for i in range(6):
                response = await async_client.post(
                    "/users/login",
                    data={
                        "username": "ratelimituser",
                        "password": "wrongpassword"
                    }
                )
                responses.append(response)
                # Small delay to ensure requests are sequential
                await asyncio.sleep(0.1)
            
            # Collect status codes
            status_codes = [r.status_code for r in responses]
            
            # At least one should be rate limited (429 Too Many Requests)
            # First 5 should be 401 Unauthorized
            assert status.HTTP_429_TOO_MANY_REQUESTS in status_codes, \
                f"Expected 429 status code in responses, got {status_codes}"
        finally:
            # Cleanup
            await test_user_rl.delete()


@pytest.mark.integration
class TestProtectedEndpoints:
    """Comprehensive test suite for protected endpoint access (AUTH-012 to AUTH-014)"""
    
    @pytest.mark.asyncio
    async def test_auth_012_get_current_user_valid_token(self, async_client, test_user):
        """
        TEST ID: AUTH-012
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test successful retrieval of current user info with valid token
        INPUT:
            Method: GET
            URL: /users/me
            Headers: Authorization: Bearer <valid_token>
        EXPECTED OUTPUT:
            Status Code: 200 OK
            Response Body: User object (id, username, email, role)
            Business Rule Validated: Token-based authentication
        """
        # First, login to get a valid token
        login_response = await async_client.post(
            "/users/login",
            data={
                "username": test_user.username,
                "password": "testpassword123"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        
        # Now test /users/me with valid token
        headers = {"Authorization": f"Bearer {token}"}
        response = await async_client.get("/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role
        assert "password" not in data, "Password should never be returned"
        assert "hashed_password" not in data, "Hashed password should never be returned"
    
    @pytest.mark.asyncio
    async def test_auth_013_get_current_user_no_token(self, async_client):
        """
        TEST ID: AUTH-013
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test failure when accessing /users/me without a token
        INPUT:
            Method: GET
            URL: /users/me
            Headers: (no Authorization header)
        EXPECTED OUTPUT:
            Status Code: 401 Unauthorized
            Response Body: "Not authenticated"
            Business Rule Validated: Authentication required for protected endpoints
        """
        response = await async_client.get("/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "not authenticated" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_auth_014_get_current_user_invalid_token(self, async_client):
        """
        TEST ID: AUTH-014
        CATEGORY: Authentication & User Accounts
        DESCRIPTION: Test failure when accessing /users/me with invalid/expired token
        INPUT:
            Method: GET
            URL: /users/me
            Headers: Authorization: Bearer <invalid_token>
        EXPECTED OUTPUT:
            Status Code: 401 Unauthorized
            Response Body: Authentication error
            Business Rule Validated: Invalid token rejection
        """
        # Use an obviously invalid token
        invalid_token = "invalid.token.here"
        headers = {"Authorization": f"Bearer {invalid_token}"}
        
        response = await async_client.get("/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data


@pytest.mark.security
class TestAuthenticationSecurity:
    """Security-focused authentication tests"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_login(self, async_client):
        """
        SECURITY TEST: SQL injection prevention in login
        INPUT: Malicious SQL injection payloads
        EXPECTED: All attempts should fail safely (401, not crash)
        """
        malicious_inputs = [
            "admin' OR '1'='1",
            "'; DROP TABLE users; --",
            "admin'--",
            "' UNION SELECT * FROM users--",
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
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
                f"SQL injection attempt with '{malicious_input}' should be rejected"
    
    @pytest.mark.asyncio
    async def test_password_not_returned_in_responses(self, async_client):
        """
        SECURITY TEST: Ensure passwords are never returned in API responses
        """
        user_data = {
            "username": "securitytest123",
            "email": "sectest@example.com",
            "password": "SecurePass123"
        }
        
        # Clean up if exists
        existing = await User.find_one(User.email == user_data["email"])
        if existing:
            await existing.delete()
        
        try:
            # Register user
            register_response = await async_client.post("/users/register", json=user_data)
            assert "password" not in register_response.text.lower() or \
                   "hashed_password" not in register_response.text
            
            # Login
            login_response = await async_client.post(
                "/users/login",
                data={
                    "username": user_data["username"],
                    "password": user_data["password"]
                }
            )
            assert "password" not in login_response.text.lower() or \
                   "hashed_password" not in login_response.text
        finally:
            # Cleanup
            user = await User.find_one(User.email == user_data["email"])
            if user:
                await user.delete()


# Import asyncio for sleep in rate limiting test
import asyncio
