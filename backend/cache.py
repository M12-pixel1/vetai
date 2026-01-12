"""
Redis cache integration for improved performance and caching.
"""

import json
import logging
from typing import Any, Optional, Union
from datetime import timedelta
import pickle

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis cache manager for caching AI results and database queries.
    
    Provides a simple interface for caching with support for TTL,
    serialization, and batch operations.
    """

    def __init__(self, redis_url: str = None, default_ttl: int = 3600):
        """
        Initialize the cache manager.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default time-to-live in seconds
        """
        self.redis_url = redis_url or "redis://localhost:6379/0"
        self.default_ttl = default_ttl
        self.redis_client = None
        self._initialize_redis()
        logger.info(f"Cache manager initialized with URL: {self.redis_url}")

    def _initialize_redis(self):
        """Initialize Redis connection."""
        try:
            import redis
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=False,  # We'll handle encoding ourselves
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except ImportError:
            logger.warning("Redis library not installed. Cache will be disabled.")
            self.redis_client = None
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to deserialize
            try:
                return pickle.loads(value)
            except:
                # Fallback to JSON
                try:
                    return json.loads(value.decode('utf-8'))
                except:
                    return value.decode('utf-8')
                    
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize: str = "pickle"
    ) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = default_ttl)
            serialize: Serialization method ('pickle' or 'json')
            
        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            # Serialize value
            if serialize == "pickle":
                serialized = pickle.dumps(value)
            elif serialize == "json":
                serialized = json.dumps(value).encode('utf-8')
            else:
                serialized = str(value).encode('utf-8')
            
            # Set with TTL
            ttl = ttl or self.default_ttl
            self.redis_client.setex(key, ttl, serialized)
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            return False

    def clear(self, pattern: str = "*") -> int:
        """
        Clear cache keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "user:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear error for pattern '{pattern}': {e}")
            return 0

    def get_or_set(
        self,
        key: str,
        callable_func,
        ttl: Optional[int] = None
    ) -> Any:
        """
        Get from cache or set if not exists (cache-aside pattern).
        
        Args:
            key: Cache key
            callable_func: Function to call if cache miss
            ttl: Time-to-live in seconds
            
        Returns:
            Cached or computed value
        """
        # Try to get from cache
        value = self.get(key)
        if value is not None:
            logger.debug(f"Cache hit for key: {key}")
            return value
        
        # Cache miss - compute value
        logger.debug(f"Cache miss for key: {key}")
        value = callable_func()
        
        # Store in cache
        self.set(key, value, ttl)
        return value

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a numeric value in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by
            
        Returns:
            New value or None if error
        """
        if not self.redis_client:
            return None
        
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key '{key}': {e}")
            return None

    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        if not self.redis_client:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info("stats")
            return {
                "enabled": True,
                "total_connections": info.get("total_connections_received"),
                "total_commands": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses"),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"enabled": True, "error": str(e)}

    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate."""
        total = hits + misses
        if total == 0:
            return 0.0
        return (hits / total) * 100

    def health_check(self) -> bool:
        """
        Check if Redis connection is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            return self.redis_client.ping()
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False
