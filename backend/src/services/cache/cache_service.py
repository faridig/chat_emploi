"""Cache service for Redis.

This service provides caching functionality using Redis for job offers,
API responses, and other data with TTL support.
"""

import json
import logging
from enum import Enum
from typing import Any

import redis


class CacheKey(str, Enum):
    """Standard cache key prefixes."""

    JOB_OFFER = "offer:"
    USER_PROFILE = "profile:"
    API_RESPONSE = "api:"
    SEARCH_RESULTS = "search:"
    STATISTICS = "stats:"


class CacheError(Exception):
    """Custom exception for cache errors."""

    pass


class CacheService:
    """Service for Redis caching operations."""

    def __init__(
        self, redis_url: str = "redis://localhost:6379", decode_responses: bool = True
    ):
        """Initialize CacheService with Redis connection.

        Args:
            redis_url: Redis connection URL
            decode_responses: Whether to decode responses as strings (default: True)
        """
        self.redis_url = redis_url
        self.decode_responses = decode_responses
        self.redis_client = None

        try:
            self.redis_client = redis.Redis.from_url(
                redis_url,
                decode_responses=decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            logging.error(f"Failed to connect to Redis at {redis_url}: {e}")
            raise CacheError(f"Failed to connect to Redis: {e}")

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
        """Set a key-value pair in cache.

        Args:
            key: Cache key
            value: Value to cache (will be stringified if not string)
            ttl_seconds: Time-to-live in seconds (optional)

        Returns:
            True if successful

        Raises:
            CacheError: If operation fails
        """
        try:
            # Convert value to string if not already
            if not isinstance(value, str):
                value = str(value)

            if ttl_seconds:
                return bool(self.redis_client.setex(key, ttl_seconds, value))
            else:
                return bool(self.redis_client.set(key, value))

        except Exception as e:
            logging.error(f"Failed to set key '{key}': {e}")
            raise CacheError(f"Failed to set key '{key}': {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache.

        Args:
            key: Cache key
            default: Default value if key doesn't exist

        Returns:
            Cached value or default
        """
        try:
            value = self.redis_client.get(key)
            if value is None:
                return default
            return value
        except Exception as e:
            logging.error(f"Failed to get key '{key}': {e}")
            raise CacheError(f"Failed to get key '{key}': {e}")

    def get_json(self, key: str, default: Any = None) -> Any:
        """Get JSON value from cache.

        Args:
            key: Cache key
            default: Default value if key doesn't exist or parsing fails

        Returns:
            Parsed JSON value or default
        """
        try:
            value = self.get(key)
            if value is None:
                return default

            # Try to parse as JSON
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            logging.warning(f"Failed to parse JSON for key '{key}', returning default")
            return default
        except CacheError:
            return default

    def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
        """Set JSON value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be serialized to JSON)
            ttl_seconds: Time-to-live in seconds (optional)

        Returns:
            True if successful
        """
        try:
            json_str = json.dumps(value)
            return self.set(key, json_str, ttl_seconds)
        except Exception as e:
            logging.error(f"Failed to set JSON for key '{key}': {e}")
            raise CacheError(f"Failed to set JSON for key '{key}': {e}")

    def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logging.error(f"Failed to delete key '{key}': {e}")
            raise CacheError(f"Failed to delete key '{key}': {e}")

    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logging.error(f"Failed to check existence of key '{key}': {e}")
            raise CacheError(f"Failed to check existence of key '{key}': {e}")

    def expire(self, key: str, ttl_seconds: int) -> bool:
        """Set TTL for existing key.

        Args:
            key: Cache key
            ttl_seconds: Time-to-live in seconds

        Returns:
            True if successful
        """
        try:
            return bool(self.redis_client.expire(key, ttl_seconds))
        except Exception as e:
            logging.error(f"Failed to set TTL for key '{key}': {e}")
            raise CacheError(f"Failed to set TTL for key '{key}': {e}")

    # Hash operations

    def hset(self, key: str, field: str, value: Any) -> bool:
        """Set field in hash.

        Args:
            key: Hash key
            field: Field name
            value: Field value

        Returns:
            True if successful
        """
        try:
            if not isinstance(value, str):
                value = str(value)
            return bool(self.redis_client.hset(key, field, value))
        except Exception as e:
            logging.error(f"Failed to hset '{key}.{field}': {e}")
            raise CacheError(f"Failed to hset '{key}.{field}': {e}")

    def hset_json(self, key: str, field: str, value: Any) -> bool:
        """Set JSON field in hash.

        Args:
            key: Hash key
            field: Field name
            value: Field value (will be serialized to JSON)

        Returns:
            True if successful
        """
        try:
            json_str = json.dumps(value)
            return self.hset(key, field, json_str)
        except Exception as e:
            logging.error(f"Failed to hset JSON for '{key}.{field}': {e}")
            raise CacheError(f"Failed to hset JSON for '{key}.{field}': {e}")

    def hget(self, key: str, field: str, default: Any = None) -> Any:
        """Get field from hash.

        Args:
            key: Hash key
            field: Field name
            default: Default value if field doesn't exist

        Returns:
            Field value or default
        """
        try:
            value = self.redis_client.hget(key, field)
            if value is None:
                return default
            return value
        except Exception as e:
            logging.error(f"Failed to hget '{key}.{field}': {e}")
            raise CacheError(f"Failed to hget '{key}.{field}': {e}")

    def hget_json(self, key: str, field: str, default: Any = None) -> Any:
        """Get JSON field from hash.

        Args:
            key: Hash key
            field: Field name
            default: Default value if field doesn't exist or parsing fails

        Returns:
            Parsed JSON value or default
        """
        try:
            value = self.hget(key, field)
            if value is None:
                return default

            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            logging.warning(
                f"Failed to parse JSON for '{key}.{field}', returning default"
            )
            return default
        except CacheError:
            return default

    def hgetall(self, key: str) -> dict[str, Any]:
        """Get all fields from hash.

        Args:
            key: Hash key

        Returns:
            Dictionary of field-value pairs
        """
        try:
            return self.redis_client.hgetall(key)
        except Exception as e:
            logging.error(f"Failed to hgetall '{key}': {e}")
            raise CacheError(f"Failed to hgetall '{key}': {e}")

    def hgetall_json(self, key: str) -> dict[str, Any]:
        """Get all fields from hash with JSON parsing.

        Args:
            key: Hash key

        Returns:
            Dictionary of parsed JSON field-value pairs
        """
        try:
            raw_dict = self.hgetall(key)
            result = {}
            for field, value in raw_dict.items():
                try:
                    result[field] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[field] = value
            return result
        except Exception as e:
            logging.error(f"Failed to hgetall JSON for '{key}': {e}")
            raise CacheError(f"Failed to hgetall JSON for '{key}': {e}")

    def hdel(self, key: str, field: str) -> bool:
        """Delete field from hash.

        Args:
            key: Hash key
            field: Field name

        Returns:
            True if successful
        """
        try:
            return bool(self.redis_client.hdel(key, field))
        except Exception as e:
            logging.error(f"Failed to hdel '{key}.{field}': {e}")
            raise CacheError(f"Failed to hdel '{key}.{field}': {e}")

    # Job offer specific methods

    def cache_job_offer(self, offer: dict[str, Any], ttl_hours: int = 24) -> bool:
        """Cache a job offer.

        Args:
            offer: Job offer dictionary (must contain 'id' field)
            ttl_hours: Time-to-live in hours (default: 24)

        Returns:
            True if successful
        """
        if "id" not in offer:
            raise ValueError("Job offer must contain 'id' field")

        offer_id = offer["id"]
        key = f"{CacheKey.JOB_OFFER.value}{offer_id}"

        return self.set_json(key, offer, ttl_seconds=ttl_hours * 3600)

    def get_cached_job_offer(self, offer_id: str) -> dict[str, Any] | None:
        """Get cached job offer by ID.

        Args:
            offer_id: Job offer ID

        Returns:
            Job offer dictionary or None if not found
        """
        key = f"{CacheKey.JOB_OFFER.value}{offer_id}"
        return self.get_json(key)

    def cache_batch_job_offers(
        self, offers: list[dict[str, Any]], ttl_hours: int = 24
    ) -> bool:
        """Cache multiple job offers in batch.

        Args:
            offers: List of job offer dictionaries
            ttl_hours: Time-to-live in hours (default: 24)

        Returns:
            True if all successful
        """
        try:
            for offer in offers:
                self.cache_job_offer(offer, ttl_hours)
            return True
        except Exception as e:
            logging.error(f"Failed to cache batch job offers: {e}")
            raise CacheError(f"Failed to cache batch job offers: {e}")

    def get_cached_job_offers(
        self, offer_ids: list[str]
    ) -> dict[str, dict[str, Any] | None]:
        """Get multiple cached job offers.

        Args:
            offer_ids: List of job offer IDs

        Returns:
            Dictionary mapping offer IDs to offer data (or None if not found)
        """
        result = {}
        for offer_id in offer_ids:
            result[offer_id] = self.get_cached_job_offer(offer_id)
        return result

    # Utility methods

    def get_keys_by_pattern(self, pattern: str) -> list[str]:
        """Get keys matching pattern.

        Args:
            pattern: Redis pattern (e.g., "offer:*")

        Returns:
            List of matching keys
        """
        try:
            keys = self.redis_client.keys(pattern)
            # Convert bytes to strings if needed
            if keys and isinstance(keys[0], bytes):
                return [k.decode("utf-8") for k in keys]
            return list(keys)
        except Exception as e:
            logging.error(f"Failed to get keys by pattern '{pattern}': {e}")
            raise CacheError(f"Failed to get keys by pattern '{pattern}': {e}")

    def clear_cache(self) -> bool:
        """Clear entire cache (flush database).

        Returns:
            True if successful
        """
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logging.error(f"Failed to clear cache: {e}")
            raise CacheError(f"Failed to clear cache: {e}")

    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter.

        Args:
            key: Counter key
            amount: Amount to increment (default: 1)

        Returns:
            New counter value
        """
        try:
            return self.redis_client.incr(key, amount)
        except Exception as e:
            logging.error(f"Failed to increment key '{key}': {e}")
            raise CacheError(f"Failed to increment key '{key}': {e}")

    def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement counter.

        Args:
            key: Counter key
            amount: Amount to decrement (default: 1)

        Returns:
            New counter value
        """
        try:
            return self.redis_client.decr(key, amount)
        except Exception as e:
            logging.error(f"Failed to decrement key '{key}': {e}")
            raise CacheError(f"Failed to decrement key '{key}': {e}")

    def get_ttl(self, key: str) -> int | None:
        """Get remaining TTL for key in seconds.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, None if key doesn't exist or has no TTL
        """
        try:
            ttl = self.redis_client.ttl(key)
            return ttl if ttl > 0 else None
        except Exception as e:
            logging.error(f"Failed to get TTL for key '{key}': {e}")
            raise CacheError(f"Failed to get TTL for key '{key}': {e}")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            # Get info from Redis
            info = self.redis_client.info()

            stats = {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
            }

            # Calculate hit rate
            hits = stats["keyspace_hits"]
            misses = stats["keyspace_misses"]
            total = hits + misses
            stats["hit_rate"] = hits / total if total > 0 else 0

            return stats
        except Exception as e:
            logging.error(f"Failed to get cache stats: {e}")
            raise CacheError(f"Failed to get cache stats: {e}")
