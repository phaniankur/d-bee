"""
Redis client utility module for handling Redis operations.
"""
import os
import json
from typing import Any, Optional, Union, Dict, List
import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RedisClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Redis connection."""
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        return self.redis.get(key)
    
    def set(self, key: str, value: Any, ex: int = None) -> bool:
        """Set value in Redis with optional expiration in seconds."""
        if not isinstance(value, (str, int, float, bool)):
            value = json.dumps(value)
        return bool(self.redis.set(key, value, ex=ex))
    
    def delete(self, *keys: str) -> int:
        """Delete one or more keys from Redis."""
        return self.redis.delete(*keys)
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        return bool(self.redis.exists(key))
    
    def expire(self, key: str, time: int) -> bool:
        """Set a key's time to live in seconds."""
        return bool(self.redis.expire(key, time))
    
    def ttl(self, key: str) -> int:
        """Get the remaining time to live of a key in seconds."""
        return self.redis.ttl(key)
    
    def hset(self, name: str, key: str, value: Any) -> int:
        """Set the string value of a hash field."""
        if not isinstance(value, (str, int, float, bool)):
            value = json.dumps(value)
        return self.redis.hset(name, key, value)
    
    def hget(self, name: str, key: str) -> Optional[Any]:
        """Get the value of a hash field."""
        value = self.redis.hget(name, key)
        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value
        
    def lrange(self, name: str, start: int, end: int) -> List[str]:
        """Get a range of elements from a list."""
        # Convert bytes to string if needed
        result = self.redis.lrange(name, start, end)
        return [item.decode('utf-8') if isinstance(item, bytes) else item for item in result]
        
    def rpush(self, name: str, *values: Any) -> int:
        """Append one or multiple values to a list."""
        # Convert all values to strings
        str_values = [str(v) for v in values]
        return self.redis.rpush(name, *str_values)
        
    def ltrim(self, name: str, start: int, end: int) -> bool:
        """Trim a list to the specified range."""
        return bool(self.redis.ltrim(name, start, end))

# Create a singleton instance
redis_client = RedisClient()
