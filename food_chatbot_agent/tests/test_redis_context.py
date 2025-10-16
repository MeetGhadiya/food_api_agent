"""
Test Suite for redis_context.py - Session Management
Tests Redis operations, fallback mechanism, TTL, and error handling
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from redis_context import RedisContextManager


class TestRedisContextManagerInitialization:
    """Test Redis client initialization"""
    
    @patch('redis_context.redis.Redis')
    def test_successful_initialization(self, mock_redis_class):
        """Test successful Redis connection"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_class.return_value = mock_redis_instance
        
        manager = RedisContextManager()
        
        assert manager.redis is not None
        assert manager.using_fallback == False
        mock_redis_instance.ping.assert_called_once()
    
    @patch('redis_context.redis.Redis')
    def test_initialization_with_connection_failure(self, mock_redis_class):
        """Test fallback activation when Redis unavailable"""
        mock_redis_class.side_effect = Exception("Connection refused")
        
        manager = RedisContextManager()
        
        assert manager.redis is None
        assert manager.using_fallback == True
        assert isinstance(manager.fallback_storage, dict)


class TestRedisContextManagerSaveOperation:
    """Test save() method"""
    
    @patch('redis_context.redis.Redis')
    def test_save_to_redis_success(self, mock_redis_class):
        """Test successful save to Redis"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.set.return_value = True
        mock_redis_class.return_value = mock_redis_instance
        
        manager = RedisContextManager()
        data = {"messages": ["Hello", "How are you?"]}
        result = manager.save("session:user123", data, ttl=300)
        
        assert result == True
        mock_redis_instance.set.assert_called_once()
    
    @patch('redis_context.redis.Redis')
    def test_save_to_fallback(self, mock_redis_class):
        """Test save to fallback storage when Redis fails"""
        mock_redis_class.side_effect = Exception("Connection refused")
        
        manager = RedisContextManager()
        data = {"messages": ["Hello"]}
        result = manager.save("session:user123", data, ttl=300)
        
        assert result == True
        assert "session:user123" in manager.fallback_storage
        assert manager.fallback_storage["session:user123"]["value"] == data
    
    @patch('redis_context.redis.Redis')
    def test_save_ttl_in_fallback(self, mock_redis_class):
        """Test TTL is properly set in fallback storage"""
        mock_redis_class.side_effect = Exception("Connection refused")
        
        manager = RedisContextManager()
        data = {"messages": ["Hello"]}
        ttl = 100
        
        before_time = time.time()
        manager.save("session:user123", data, ttl=ttl)
        after_time = time.time()
        
        stored_data = manager.fallback_storage["session:user123"]
        assert "expires_at" in stored_data
        # Check expiration is approximately correct (within 5 seconds)
        expected_expiry = before_time + ttl
        assert abs(stored_data["expires_at"] - expected_expiry) < 5


class TestRedisContextManagerGetOperation:
    """Test get() method"""
    
    @patch('redis_context.redis.Redis')
    def test_get_from_redis_success(self, mock_redis_class):
        """Test successful get from Redis"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        test_data = '{"messages": ["Hello", "World"]}'
        mock_redis_instance.get.return_value = test_data.encode('utf-8')
        mock_redis_class.return_value = mock_redis_instance
        
        manager = RedisContextManager()
        result = manager.get("session:user123")
        
        assert result == {"messages": ["Hello", "World"]}
        mock_redis_instance.get.assert_called_once_with("session:user123")
    
    @patch('redis_context.redis.Redis')
    def test_get_from_fallback(self, mock_redis_class):
        """Test get from fallback storage"""
        mock_redis_class.side_effect = Exception("Connection refused")
        
        manager = RedisContextManager()
        data = {"messages": ["Test"]}
        manager.save("session:user123", data, ttl=300)
        
        result = manager.get("session:user123")
        assert result == data
    
    @patch('redis_context.redis.Redis')
    def test_get_expired_from_fallback(self, mock_redis_class):
        """Test getting expired data from fallback returns None"""
        mock_redis_class.side_effect = Exception("Connection refused")
        
        manager = RedisContextManager()
        data = {"messages": ["Test"]}
        
        # Manually set expired data
        manager.fallback_storage["session:user123"] = {
            "value": data,
            "expires_at": time.time() - 10  # Expired 10 seconds ago
        }
        
        result = manager.get("session:user123")
        assert result is None
        assert "session:user123" not in manager.fallback_storage  # Should be deleted
    
    @patch('redis_context.redis.Redis')
    def test_get_nonexistent_key(self, mock_redis_class):
        """Test getting non-existent key returns None"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.return_value = None
        mock_redis_class.return_value = mock_redis_instance
        
        manager = RedisContextManager()
        result = manager.get("session:nonexistent")
        
        assert result is None


class TestRedisContextManagerDeleteOperation:
    """Test delete() method"""
    
    @patch('redis_context.redis.Redis')
    def test_delete_from_redis(self, mock_redis_class):
        """Test delete from Redis"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.delete.return_value = 1
        mock_redis_class.return_value = mock_redis_instance
        
        manager = RedisContextManager()
        result = manager.delete("session:user123")
        
        assert result == True
        mock_redis_instance.delete.assert_called_once_with("session:user123")
    
    @patch('redis_context.redis.Redis')
    def test_delete_from_fallback(self, mock_redis_class):
        """Test delete from fallback storage"""
        mock_redis_class.side_effect = Exception("Connection refused")
        
        manager = RedisContextManager()
        manager.save("session:user123", {"test": "data"}, ttl=300)
        
        assert "session:user123" in manager.fallback_storage
        result = manager.delete("session:user123")
        
        assert result == True
        assert "session:user123" not in manager.fallback_storage


class TestRedisContextManagerHealthCheck:
    """Test health_check() method"""
    
    @patch('redis_context.redis.Redis')
    def test_health_check_redis_up(self, mock_redis_class):
        """Test health check when Redis is available"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_class.return_value = mock_redis_instance
        
        manager = RedisContextManager()
        result = manager.health_check()
        
        assert result == {"status": "redis", "available": True}
    
    @patch('redis_context.redis.Redis')
    def test_health_check_fallback(self, mock_redis_class):
        """Test health check when using fallback"""
        mock_redis_class.side_effect = Exception("Connection refused")
        
        manager = RedisContextManager()
        result = manager.health_check()
        
        assert result == {"status": "in-memory", "available": True}


class TestRedisContextManagerRetryLogic:
    """Test retry logic with exponential backoff"""
    
    @patch('redis_context.redis.Redis')
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_retry_on_transient_failure(self, mock_sleep, mock_redis_class):
        """Test retry logic when operation fails temporarily"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        
        # Fail twice, succeed on third attempt
        mock_redis_instance.set.side_effect = [
            Exception("Temporary failure"),
            Exception("Temporary failure"),
            True
        ]
        mock_redis_class.return_value = mock_redis_instance
        
        manager = RedisContextManager()
        result = manager.save("session:user123", {"test": "data"}, ttl=300)
        
        # Should eventually succeed
        assert result == True
        # Should have tried 3 times
        assert mock_redis_instance.set.call_count == 3
        # Should have slept twice (between retries)
        assert mock_sleep.call_count == 2


class TestRedisContextManagerExistsOperation:
    """Test exists() method"""
    
    @patch('redis_context.redis.Redis')
    def test_exists_in_redis(self, mock_redis_class):
        """Test checking if key exists in Redis"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.exists.return_value = 1
        mock_redis_class.return_value = mock_redis_instance
        
        manager = RedisContextManager()
        result = manager.exists("session:user123")
        
        assert result == True
    
    @patch('redis_context.redis.Redis')
    def test_exists_in_fallback(self, mock_redis_class):
        """Test checking if key exists in fallback"""
        mock_redis_class.side_effect = Exception("Connection refused")
        
        manager = RedisContextManager()
        manager.save("session:user123", {"test": "data"}, ttl=300)
        
        assert manager.exists("session:user123") == True
        assert manager.exists("session:nonexistent") == False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
