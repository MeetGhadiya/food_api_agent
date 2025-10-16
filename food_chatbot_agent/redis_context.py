"""
FoodieExpress Agent - Redis Context Manager
===========================================
Production-ready Redis session storage with TTL, retry logic, and graceful fallbacks

This module provides a clean interface for storing and retrieving conversation
context, pending orders, and user state in Redis with automatic expiration.

Version: 4.0
Author: Meet Ghadiya
Date: October 2025
"""

import json
import time
from typing import Any, Optional, Dict
from config import config


class RedisContextManager:
    """
    Manages conversation context and state in Redis.
    
    Features:
    - Automatic TTL (Time-To-Live) expiration
    - Retry logic for network failures
    - Graceful fallback to in-memory storage
    - JSON serialization for complex data types
    - Connection pooling for performance
    """
    
    def __init__(self):
        """Initialize Redis connection with fallback support"""
        self.redis_client = None
        self.fallback_storage: Dict[str, Any] = {}  # In-memory fallback
        self.is_connected = False
        
        if config.REDIS_ENABLED:
            self._initialize_redis()
        else:
            print("ℹ️  Redis disabled in configuration - using in-memory storage")
    
    def _initialize_redis(self):
        """Initialize Redis client with error handling"""
        try:
            import redis
            
            self.redis_client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                password=config.REDIS_PASSWORD,
                db=config.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=config.REDIS_CONNECTION_TIMEOUT,
                socket_keepalive=True,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection with ping
            self.redis_client.ping()
            self.is_connected = True
            print(f"✅ Redis connected: {config.REDIS_HOST}:{config.REDIS_PORT}")
            
        except ImportError:
            print("⚠️  Redis module not installed - using in-memory storage")
            print("   Install with: pip install redis")
            self.redis_client = None
            self.is_connected = False
            
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}")
            print("   Falling back to in-memory storage")
            self.redis_client = None
            self.is_connected = False
    
    def _retry_operation(self, operation, max_retries=3, backoff_factor=0.5):
        """
        Retry a Redis operation with exponential backoff.
        
        Args:
            operation: Lambda function to execute
            max_retries: Maximum number of retry attempts
            backoff_factor: Multiplier for exponential backoff
            
        Returns:
            Result of the operation or None on failure
        """
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"❌ Redis operation failed after {max_retries} attempts: {e}")
                    return None
                
                # Exponential backoff
                sleep_time = backoff_factor * (2 ** attempt)
                print(f"⚠️  Redis operation failed (attempt {attempt + 1}/{max_retries}), retrying in {sleep_time}s...")
                time.sleep(sleep_time)
        
        return None
    
    def save(self, user_id: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Save data to Redis with TTL expiration.
        
        Args:
            user_id: User identifier
            key: Data key (e.g., 'last_entity', 'pending_order', 'chat_history')
            value: Data to store (will be JSON serialized)
            ttl: Time to live in seconds (default from config)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if ttl is None:
            ttl = config.REDIS_TTL
        
        redis_key = f"session:{user_id}:{key}"
        
        if self.is_connected and self.redis_client:
            # Try Redis with retry logic
            def operation():
                serialized_value = json.dumps(value)
                self.redis_client.setex(redis_key, ttl, serialized_value)
                return True
            
            result = self._retry_operation(operation)
            if result:
                print(f"✅ Saved to Redis: {redis_key} (TTL={ttl}s)")
                return True
        
        # Fallback to in-memory storage
        self.fallback_storage[redis_key] = {
            'value': value,
            'expires_at': time.time() + ttl
        }
        print(f"💾 Saved to memory (fallback): {redis_key}")
        return True
    
    def get(self, user_id: str, key: str, default: Any = None) -> Any:
        """
        Retrieve data from Redis.
        
        Args:
            user_id: User identifier
            key: Data key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        redis_key = f"session:{user_id}:{key}"
        
        if self.is_connected and self.redis_client:
            # Try Redis with retry logic
            def operation():
                data = self.redis_client.get(redis_key)
                if data and isinstance(data, str):
                    return json.loads(data)
                return None
            
            result = self._retry_operation(operation)
            if result is not None:
                print(f"📖 Retrieved from Redis: {redis_key}")
                return result
        
        # Fallback to in-memory storage
        if redis_key in self.fallback_storage:
            stored_data = self.fallback_storage[redis_key]
            
            # Check if expired
            if time.time() < stored_data['expires_at']:
                print(f"📖 Retrieved from memory (fallback): {redis_key}")
                return stored_data['value']
            else:
                # Expired - remove it
                del self.fallback_storage[redis_key]
                print(f"⏰ Expired in memory: {redis_key}")
        
        return default
    
    def delete(self, user_id: str, key: Optional[str] = None) -> bool:
        """
        Delete data from Redis.
        
        Args:
            user_id: User identifier
            key: Specific key to delete, or None to delete all user data
            
        Returns:
            bool: True if successful
        """
        if self.is_connected and self.redis_client:
            # Try Redis with retry logic
            def operation():
                if key:
                    redis_key = f"session:{user_id}:{key}"
                    self.redis_client.delete(redis_key)
                    print(f"🗑️  Deleted from Redis: {redis_key}")
                else:
                    # Delete all keys for this user
                    pattern = f"session:{user_id}:*"
                    keys_list = self.redis_client.keys(pattern)
                    if keys_list and isinstance(keys_list, list) and len(keys_list) > 0:
                        self.redis_client.delete(*keys_list)
                        print(f"🗑️  Deleted {len(keys_list)} keys from Redis for user: {user_id}")
                return True
            
            result = self._retry_operation(operation)
            if result:
                return True
        
        # Fallback to in-memory storage
        if key:
            redis_key = f"session:{user_id}:{key}"
            if redis_key in self.fallback_storage:
                del self.fallback_storage[redis_key]
                print(f"🗑️  Deleted from memory (fallback): {redis_key}")
        else:
            # Delete all keys for this user
            keys_to_delete = [k for k in self.fallback_storage.keys() if k.startswith(f"session:{user_id}:")]
            for k in keys_to_delete:
                del self.fallback_storage[k]
            print(f"🗑️  Deleted {len(keys_to_delete)} keys from memory for user: {user_id}")
        
        return True
    
    def exists(self, user_id: str, key: str) -> bool:
        """
        Check if a key exists in Redis.
        
        Args:
            user_id: User identifier
            key: Data key
            
        Returns:
            bool: True if key exists and not expired
        """
        redis_key = f"session:{user_id}:{key}"
        
        if self.is_connected and self.redis_client:
            def operation():
                return self.redis_client.exists(redis_key) > 0
            
            result = self._retry_operation(operation)
            if result is not None:
                return result
        
        # Fallback to in-memory storage
        if redis_key in self.fallback_storage:
            stored_data = self.fallback_storage[redis_key]
            return time.time() < stored_data['expires_at']
        
        return False
    
    def get_ttl(self, user_id: str, key: str) -> Optional[int]:
        """
        Get remaining TTL for a key in seconds.
        
        Args:
            user_id: User identifier
            key: Data key
            
        Returns:
            int: Remaining TTL in seconds, or None if key doesn't exist
        """
        redis_key = f"session:{user_id}:{key}"
        
        if self.is_connected and self.redis_client:
            def operation():
                ttl = self.redis_client.ttl(redis_key)
                return ttl if ttl > 0 else None
            
            return self._retry_operation(operation)
        
        # Fallback to in-memory storage
        if redis_key in self.fallback_storage:
            stored_data = self.fallback_storage[redis_key]
            remaining = int(stored_data['expires_at'] - time.time())
            return remaining if remaining > 0 else None
        
        return None
    
    def extend_ttl(self, user_id: str, key: str, additional_seconds: int) -> bool:
        """
        Extend the TTL of an existing key.
        
        Args:
            user_id: User identifier
            key: Data key
            additional_seconds: Seconds to add to current TTL
            
        Returns:
            bool: True if successful
        """
        redis_key = f"session:{user_id}:{key}"
        
        if self.is_connected and self.redis_client:
            def operation():
                current_ttl = self.redis_client.ttl(redis_key)
                if current_ttl > 0:
                    new_ttl = current_ttl + additional_seconds
                    self.redis_client.expire(redis_key, new_ttl)
                    print(f"⏱️  Extended TTL for {redis_key} to {new_ttl}s")
                    return True
                return False
            
            return self._retry_operation(operation) or False
        
        # Fallback to in-memory storage
        if redis_key in self.fallback_storage:
            self.fallback_storage[redis_key]['expires_at'] += additional_seconds
            print(f"⏱️  Extended TTL for {redis_key} in memory")
            return True
        
        return False
    
    def get_all_keys(self, user_id: str) -> list[str]:
        """
        Get all keys for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            list: List of key names (without the session prefix)
        """
        pattern = f"session:{user_id}:*"
        keys = []
        
        if self.is_connected and self.redis_client:
            def operation():
                redis_keys = self.redis_client.keys(pattern)
                # Remove the prefix from keys
                return [k.replace(f"session:{user_id}:", "") for k in redis_keys]
            
            result = self._retry_operation(operation)
            if result:
                return result
        
        # Fallback to in-memory storage
        for k in self.fallback_storage.keys():
            if k.startswith(pattern[:-1]):  # Remove the * from pattern
                stored_data = self.fallback_storage[k]
                # Check if not expired
                if time.time() < stored_data['expires_at']:
                    keys.append(k.replace(f"session:{user_id}:", ""))
        
        return keys
    
    def cleanup_expired(self):
        """Clean up expired keys from in-memory fallback storage"""
        current_time = time.time()
        expired_keys = [
            k for k, v in self.fallback_storage.items()
            if current_time >= v['expires_at']
        ]
        
        for key in expired_keys:
            del self.fallback_storage[key]
        
        if expired_keys:
            print(f"🧹 Cleaned up {len(expired_keys)} expired keys from memory")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check Redis connection health.
        
        Returns:
            dict: Health status information
        """
        if not self.is_connected or not self.redis_client:
            return {
                "status": "disabled",
                "message": "Redis is disabled or not connected",
                "fallback": "in-memory storage"
            }
        
        try:
            # Test connection
            self.redis_client.ping()
            
            # Get Redis info
            info = self.redis_client.info()
            
            return {
                "status": "healthy",
                "host": f"{config.REDIS_HOST}:{config.REDIS_PORT}",
                "db": config.REDIS_DB,
                "connected_clients": info.get('connected_clients', 0),
                "used_memory_human": info.get('used_memory_human', 'N/A'),
                "uptime_in_seconds": info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "fallback": "in-memory storage"
            }


# Create a singleton instance
redis_context = RedisContextManager()


# Convenience functions for backward compatibility
def save_to_redis(user_id: str, key: str, value: Any, ttl: int = None) -> bool:
    """Save data to Redis (convenience function)"""
    return redis_context.save(user_id, key, value, ttl)


def get_from_redis(user_id: str, key: str, default: Any = None) -> Any:
    """Get data from Redis (convenience function)"""
    return redis_context.get(user_id, key, default)


def delete_from_redis(user_id: str, key: Optional[str] = None) -> bool:
    """Delete data from Redis (convenience function)"""
    return redis_context.delete(user_id, key)


if __name__ == "__main__":
    # Test the Redis context manager
    print("\n🧪 Testing Redis Context Manager...")
    print("=" * 60)
    
    # Health check
    health = redis_context.health_check()
    print(f"\n📊 Health Check:")
    for k, v in health.items():
        print(f"  • {k}: {v}")
    
    # Test save/get
    print(f"\n🧪 Test 1: Save and retrieve data")
    redis_context.save("test_user", "test_key", {"message": "Hello, Redis!"}, ttl=300)
    result = redis_context.get("test_user", "test_key")
    print(f"  Result: {result}")
    
    # Test TTL
    print(f"\n🧪 Test 2: Check TTL")
    ttl = redis_context.get_ttl("test_user", "test_key")
    print(f"  Remaining TTL: {ttl}s")
    
    # Test exists
    print(f"\n🧪 Test 3: Check if key exists")
    exists = redis_context.exists("test_user", "test_key")
    print(f"  Exists: {exists}")
    
    # Test get all keys
    print(f"\n🧪 Test 4: Get all keys for user")
    keys = redis_context.get_all_keys("test_user")
    print(f"  Keys: {keys}")
    
    # Cleanup
    print(f"\n🧪 Test 5: Delete data")
    redis_context.delete("test_user")
    exists_after = redis_context.exists("test_user", "test_key")
    print(f"  Exists after delete: {exists_after}")
    
    print("\n" + "=" * 60)
    print("✅ Redis Context Manager tests complete!")
