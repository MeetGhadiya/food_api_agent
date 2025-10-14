"""
Unit Tests for Security Module
Tests password hashing, verification, and JWT token generation
"""

import pytest
from datetime import timedelta
from jose import jwt
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)


class TestPasswordHashing:
    """Test suite for password hashing and verification"""
    
    def test_password_hashing_creates_different_hash(self):
        """Test that hashing a password creates a different string"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert password != hashed
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # Bcrypt hash prefix
    
    def test_same_password_creates_different_hashes(self):
        """Test that hashing the same password twice creates different hashes (salt)"""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different due to random salt
    
    def test_verify_password_with_correct_password(self):
        """Test that verification succeeds with the correct password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) == True
    
    def test_verify_password_with_incorrect_password(self):
        """Test that verification fails with an incorrect password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) == False
    
    def test_empty_password_handling(self):
        """Test that empty passwords are handled correctly"""
        password = ""
        hashed = hash_password(password)
        
        assert verify_password("", hashed) == True
        assert verify_password("anything", hashed) == False
    
    def test_long_password_truncation(self):
        """Test that passwords longer than 72 bytes are truncated correctly"""
        # Create a password longer than 72 bytes
        long_password = "a" * 100
        hashed = hash_password(long_password)
        
        # Should verify successfully with the same long password
        assert verify_password(long_password, hashed) == True
    
    def test_unicode_password_support(self):
        """Test that unicode characters in passwords work correctly"""
        password = "пароль123🔐"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) == True
        assert verify_password("password123🔒", hashed) == False


class TestJWTTokens:
    """Test suite for JWT token creation and validation"""
    
    def test_create_access_token_basic(self):
        """Test basic JWT token creation"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_token_contains_correct_data(self):
        """Test that the token contains the correct user data"""
        username = "testuser"
        data = {"sub": username}
        token = create_access_token(data)
        
        # Decode token (without verification for testing)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert decoded["sub"] == username
        assert "exp" in decoded  # Expiration should be set
    
    def test_token_with_custom_expiration(self):
        """Test token creation with custom expiration time"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=expires_delta)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Token should have exp claim
        assert "exp" in decoded
    
    def test_token_with_additional_claims(self):
        """Test that additional claims are preserved in the token"""
        data = {
            "sub": "testuser",
            "role": "admin",
            "email": "test@example.com"
        }
        token = create_access_token(data)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "admin"
        assert decoded["email"] == "test@example.com"
    
    def test_token_signature_validation(self):
        """Test that tokens with invalid signatures are rejected"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # Tamper with the token
        tampered_token = token[:-10] + "TAMPERED!"
        
        # Should raise an error when trying to decode with verification
        with pytest.raises(Exception):
            jwt.decode(tampered_token, SECRET_KEY, algorithms=[ALGORITHM])


class TestSecurityConstants:
    """Test security configuration constants"""
    
    def test_secret_key_exists(self):
        """Test that SECRET_KEY is configured"""
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) > 0
    
    def test_algorithm_is_correct(self):
        """Test that ALGORITHM is set to a secure value"""
        assert ALGORITHM == "HS256"


@pytest.mark.security
class TestSecurityVulnerabilities:
    """Security-focused tests to catch potential vulnerabilities"""
    
    def test_timing_attack_resistance(self):
        """Test that password verification is resistant to timing attacks"""
        import time
        
        password = "testpassword123"
        hashed = hash_password(password)
        
        # Time correct password verification
        start = time.perf_counter()
        verify_password(password, hashed)
        correct_time = time.perf_counter() - start
        
        # Time incorrect password verification
        start = time.perf_counter()
        verify_password("wrongpassword", hashed)
        incorrect_time = time.perf_counter() - start
        
        # Times should be relatively similar (within 50% difference)
        # Note: This is a basic test; real timing attack resistance is complex
        time_diff_ratio = abs(correct_time - incorrect_time) / max(correct_time, incorrect_time)
        assert time_diff_ratio < 0.5, "Potential timing attack vulnerability"
    
    def test_password_hash_not_reversible(self):
        """Test that password hashes cannot be reversed"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        # Hash should not contain the original password
        assert password not in hashed
        assert password.encode() not in hashed.encode()
    
    def test_weak_password_detection(self):
        """Test handling of weak passwords (should still hash them)"""
        weak_passwords = ["123", "password", "abc", ""]
        
        for weak_pw in weak_passwords:
            hashed = hash_password(weak_pw)
            # Should still create a hash (validation should happen at API level)
            assert verify_password(weak_pw, hashed) == True
