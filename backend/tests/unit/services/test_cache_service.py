"""Test suite for Cache service.

Tests the CacheService for Redis caching of job offers and other data.
Following TDD approach - tests should fail initially.
"""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest
import redis
from services.cache.cache_service import CacheError, CacheService


class TestCacheService:
    """Test suite for CacheService."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        with patch("services.cache.cache_service.redis") as mock_redis_module:
            # Mock Redis client
            mock_client = Mock()

            # Mock Redis.from_url to return mock client
            mock_redis_module.Redis.from_url.return_value = mock_client

            # Mock Redis methods
            mock_client.set = Mock(return_value=True)
            mock_client.get = Mock()
            mock_client.delete = Mock(return_value=1)
            mock_client.exists = Mock()
            mock_client.expire = Mock(return_value=True)
            mock_client.setex = Mock(return_value=True)
            mock_client.hset = Mock(return_value=1)
            mock_client.hget = Mock()
            mock_client.hgetall = Mock()
            mock_client.hdel = Mock(return_value=1)
            mock_client.keys = Mock()
            mock_client.flushdb = Mock()
            mock_client.ping = Mock()
            mock_client.incr = Mock()
            mock_client.decr = Mock()
            mock_client.ttl = Mock()
            mock_client.info = Mock()

            yield mock_redis_module, mock_client

    @pytest.fixture
    def sample_job_offer(self):
        """Sample job offer data for caching."""
        return {
            "id": "offer_123",
            "title": "Python Developer",
            "company": "Tech Corp",
            "location": "Paris",
            "description": "Looking for Python developer",
            "publication_date": "2026-01-28",
        }

    @pytest.fixture
    def cache_service(self, mock_redis):
        """Create CacheService instance with mocked dependencies."""
        redis_mock, mock_client = mock_redis
        return CacheService(redis_url="redis://localhost:6379")

    def test_init_with_redis_url(self, mock_redis):
        """Test CacheService initialization."""
        # Arrange
        redis_mock, mock_client = mock_redis

        # Act
        service = CacheService(redis_url="redis://localhost:6379")

        # Assert
        assert service.redis_url == "redis://localhost:6379"
        redis_mock.Redis.from_url.assert_called_once()
        # Check arguments
        call_args = redis_mock.Redis.from_url.call_args
        assert call_args[0][0] == "redis://localhost:6379"
        assert call_args[1]["decode_responses"]

    def test_set_get_string(self, cache_service, mock_redis):
        """Test setting and getting string values."""
        # Arrange
        _, mock_client = mock_redis
        key = "test_key"
        value = "test_value"

        mock_client.get.return_value = value  # Return string, not bytes

        # Act - Set
        cache_service.set(key, value)

        # Act - Get
        result = cache_service.get(key)

        # Assert
        assert result == value
        mock_client.set.assert_called_once_with(key, value)
        mock_client.get.assert_called_once_with(key)

    def test_set_get_json(self, cache_service, mock_redis, sample_job_offer):
        """Test setting and getting JSON values."""
        # Arrange
        _, mock_client = mock_redis
        key = "offer_123"

        # Mock get to return JSON string
        mock_client.get.return_value = json.dumps(
            sample_job_offer
        )  # Return string, not bytes

        # Act - Set JSON
        cache_service.set_json(key, sample_job_offer)

        # Act - Get JSON
        result = cache_service.get_json(key)

        # Assert
        assert result == sample_job_offer
        mock_client.set.assert_called_once()
        mock_client.get.assert_called_once_with(key)

    def test_set_with_ttl(self, cache_service, mock_redis):
        """Test setting value with TTL."""
        # Arrange
        _, mock_client = mock_redis
        key = "key_with_ttl"
        value = "value"
        ttl_seconds = 3600  # 1 hour

        # Act
        cache_service.set(key, value, ttl_seconds=ttl_seconds)

        # Assert
        mock_client.setex.assert_called_once_with(key, ttl_seconds, value)

    def test_delete_key(self, cache_service, mock_redis):
        """Test deleting a key."""
        # Arrange
        _, mock_client = mock_redis
        key = "key_to_delete"

        # Act
        result = cache_service.delete(key)

        # Assert
        assert result is True
        mock_client.delete.assert_called_once_with(key)

    def test_key_exists(self, cache_service, mock_redis):
        """Test checking if key exists."""
        # Arrange
        _, mock_client = mock_redis
        key = "existing_key"
        mock_client.exists.return_value = 1

        # Act
        exists = cache_service.exists(key)

        # Assert
        assert exists is True
        mock_client.exists.assert_called_once_with(key)

    def test_key_not_exists(self, cache_service, mock_redis):
        """Test checking if key doesn't exist."""
        # Arrange
        _, mock_client = mock_redis
        key = "non_existing_key"
        mock_client.exists.return_value = 0

        # Act
        exists = cache_service.exists(key)

        # Assert
        assert exists is False

    def test_get_with_default(self, cache_service, mock_redis):
        """Test getting value with default if key doesn't exist."""
        # Arrange
        _, mock_client = mock_redis
        key = "missing_key"
        default = "default_value"
        mock_client.get.return_value = None

        # Act
        result = cache_service.get(key, default=default)

        # Assert
        assert result == default
        mock_client.get.assert_called_once_with(key)

    def test_hash_operations(self, cache_service, mock_redis):
        """Test hash (dictionary) operations."""
        # Arrange
        _, mock_client = mock_redis
        key = "user:123"
        field = "profile"
        value = {"name": "John", "age": 30}

        # Mock hget to return JSON
        mock_client.hget.return_value = json.dumps(value)  # Return string, not bytes

        # Act - Set hash field
        cache_service.hset_json(key, field, value)

        # Act - Get hash field
        result = cache_service.hget_json(key, field)

        # Assert
        assert result == value
        mock_client.hset.assert_called_once()
        mock_client.hget.assert_called_once_with(key, field)

    def test_get_all_hash(self, cache_service, mock_redis):
        """Test getting all fields from a hash."""
        # Arrange
        _, mock_client = mock_redis
        key = "user:123"
        hash_data = {"profile": '{"name": "John"}', "settings": '{"theme": "dark"}'}
        mock_client.hgetall.return_value = hash_data

        # Act
        result = cache_service.hgetall_json(key)

        # Assert
        assert "profile" in result
        assert "settings" in result
        assert result["profile"]["name"] == "John"
        mock_client.hgetall.assert_called_once_with(key)

    def test_cache_job_offer(self, cache_service, mock_redis, sample_job_offer):
        """Test caching job offer with standard TTL."""
        # Arrange
        _, mock_client = mock_redis
        offer_id = sample_job_offer["id"]

        # Mock setex for TTL
        mock_client.setex.return_value = True

        # Act
        result = cache_service.cache_job_offer(sample_job_offer, ttl_hours=24)

        # Assert
        assert result is True
        mock_client.setex.assert_called_once()
        call_args = mock_client.setex.call_args
        # CacheKey.JOB_OFFER is an Enum, need to check for its value
        assert f"offer:{offer_id}" in str(call_args[0][0])  # Check the key
        assert call_args[0][1] == 24 * 3600  # TTL in seconds

    def test_get_cached_job_offer(self, cache_service, mock_redis, sample_job_offer):
        """Test retrieving cached job offer."""
        # Arrange
        _, mock_client = mock_redis
        offer_id = sample_job_offer["id"]

        mock_client.get.return_value = json.dumps(
            sample_job_offer
        )  # Return string, not bytes

        # Act
        result = cache_service.get_cached_job_offer(offer_id)

        # Assert
        assert result == sample_job_offer
        # CacheKey.JOB_OFFER is an Enum, need to check for its value
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == f"offer:{offer_id}"  # Check the key

    def test_cache_batch_job_offers(self, cache_service, mock_redis):
        """Test caching multiple job offers in batch."""
        # Arrange
        _, mock_client = mock_redis
        offers = [
            {"id": "offer_1", "title": "Job 1"},
            {"id": "offer_2", "title": "Job 2"},
            {"id": "offer_3", "title": "Job 3"},
        ]

        # Act
        result = cache_service.cache_batch_job_offers(offers, ttl_hours=24)

        # Assert
        assert result is True
        assert mock_client.setex.call_count == len(offers)

    def test_get_keys_by_pattern(self, cache_service, mock_redis):
        """Test getting keys by pattern."""
        # Arrange
        _, mock_client = mock_redis
        pattern = "offer:*"
        keys = ["offer:1", "offer:2", "offer:3"]
        mock_client.keys.return_value = [k.encode("utf-8") for k in keys]

        # Act
        result = cache_service.get_keys_by_pattern(pattern)

        # Assert
        assert len(result) == len(keys)
        assert "offer:1" in result
        mock_client.keys.assert_called_once_with(pattern)

    def test_clear_cache(self, cache_service, mock_redis):
        """Test clearing entire cache."""
        # Arrange
        _, mock_client = mock_redis

        # Act
        result = cache_service.clear_cache()

        # Assert
        assert result is True
        mock_client.flushdb.assert_called_once()

    def test_increment_counter(self, cache_service, mock_redis):
        """Test incrementing counter."""
        # Arrange
        _, mock_client = mock_redis
        key = "counter:requests"
        mock_client.incr = Mock(return_value=5)

        # Act
        result = cache_service.increment(key)

        # Assert
        assert result == 5
        mock_client.incr.assert_called_once_with(
            key, 1
        )  # increment() calls incr(key, amount=1)

    def test_cache_miss_stats(self, cache_service, mock_redis):
        """Test cache miss statistics."""
        # Arrange
        _, mock_client = mock_redis
        key = "offer:missing"
        mock_client.get.return_value = None

        # Act - Try to get missing key
        result = cache_service.get(key)

        # Assert
        assert result is None
        # Could track stats here

    def test_connection_error_handling(self, cache_service, mock_redis):
        """Test handling of Redis connection errors."""
        # Arrange
        _, mock_client = mock_redis
        mock_client.get.side_effect = ConnectionError("Redis connection failed")

        # Act & Assert
        with pytest.raises(CacheError, match="Redis connection failed"):
            cache_service.get("test_key")

    def test_get_ttl_key_exists(self, cache_service, mock_redis):
        """Test getting TTL for existing key."""
        # Arrange
        _, mock_client = mock_redis
        key = "key_with_ttl"
        ttl_value = 300  # 5 minutes

        mock_client.ttl.return_value = ttl_value

        # Act
        result = cache_service.get_ttl(key)

        # Assert
        assert result == ttl_value
        mock_client.ttl.assert_called_once_with(key)

    def test_get_ttl_key_no_ttl(self, cache_service, mock_redis):
        """Test getting TTL for key with no TTL (should return None)."""
        # Arrange
        _, mock_client = mock_redis
        key = "key_no_ttl"

        mock_client.ttl.return_value = -1  # No TTL

        # Act
        result = cache_service.get_ttl(key)

        # Assert
        assert result is None
        mock_client.ttl.assert_called_once_with(key)

    def test_get_ttl_key_not_exists(self, cache_service, mock_redis):
        """Test getting TTL for non-existent key (should return None)."""
        # Arrange
        _, mock_client = mock_redis
        key = "non_existent_key"

        mock_client.ttl.return_value = -2  # Key doesn't exist

        # Act
        result = cache_service.get_ttl(key)

        # Assert
        assert result is None
        mock_client.ttl.assert_called_once_with(key)

    def test_decrement_counter(self, cache_service, mock_redis):
        """Test decrementing counter."""
        # Arrange
        _, mock_client = mock_redis
        key = "counter:requests"

        mock_client.decr.return_value = 4

        # Act
        result = cache_service.decrement(key, amount=2)

        # Assert
        assert result == 4
        mock_client.decr.assert_called_once_with(key, 2)

    def test_cache_job_offer_missing_id(self, cache_service, mock_redis):
        """Test caching job offer without ID (should raise ValueError)."""
        # Arrange
        offer = {"title": "Job without ID"}  # Missing 'id' field

        # Act & Assert
        with pytest.raises(ValueError, match="Job offer must contain 'id' field"):
            cache_service.cache_job_offer(offer)

    def test_set_with_non_string_value(self, cache_service, mock_redis):
        """Test setting non-string value (should be converted to string)."""
        # Arrange
        _, mock_client = mock_redis
        key = "test_key"
        value = 123  # Integer, not string

        mock_client.set.return_value = True

        # Act
        result = cache_service.set(key, value)

        # Assert
        assert result is True
        # Should convert integer to string
        mock_client.set.assert_called_once_with(key, "123")

    def test_hset_with_non_string_value(self, cache_service, mock_redis):
        """Test hset with non-string value (should be converted to string)."""
        # Arrange
        _, mock_client = mock_redis
        key = "hash_key"
        field = "field1"
        value = 456  # Integer, not string

        mock_client.hset.return_value = 1

        # Act
        result = cache_service.hset(key, field, value)

        # Assert
        assert result is True
        # Should convert integer to string
        mock_client.hset.assert_called_once_with(key, field, "456")

    def test_get_json_with_invalid_json(self, cache_service, mock_redis):
        """Test getting JSON with invalid JSON string (should return default)."""
        # Arrange
        _, mock_client = mock_redis
        key = "invalid_json_key"
        default = {"default": "value"}

        # Mock get to return invalid JSON
        mock_client.get.return_value = "not valid json"

        # Act
        result = cache_service.get_json(key, default=default)

        # Assert
        assert result == default
        mock_client.get.assert_called_once_with(key)

    def test_hget_json_with_invalid_json(self, cache_service, mock_redis):
        """Test hget_json with invalid JSON string (should return default)."""
        # Arrange
        _, mock_client = mock_redis
        key = "hash_key"
        field = "invalid_field"
        default = {"default": "value"}

        # Mock hget to return invalid JSON
        mock_client.hget.return_value = "not valid json"

        # Act
        result = cache_service.hget_json(key, field, default=default)

        # Assert
        assert result == default
        mock_client.hget.assert_called_once_with(key, field)

    def test_hgetall_with_empty_hash(self, cache_service, mock_redis):
        """Test hgetall with empty hash."""
        # Arrange
        _, mock_client = mock_redis
        key = "empty_hash"

        # Mock hgetall to return empty dict
        mock_client.hgetall.return_value = {}

        # Act
        result = cache_service.hgetall(key)

        # Assert
        assert result == {}
        mock_client.hgetall.assert_called_once_with(key)

    def test_expire_key(self, cache_service, mock_redis):
        """Test setting expiration on existing key."""
        # Arrange
        _, mock_client = mock_redis
        key = "expiring_key"
        ttl_seconds = 600

        # Mock successful expire
        mock_client.expire.return_value = True

        # Act
        result = cache_service.expire(key, ttl_seconds)

        # Assert
        assert result is True
        mock_client.expire.assert_called_once_with(key, ttl_seconds)

    def test_init_connection_error(self):
        """Test CacheService initialization with connection error."""
        # Arrange
        invalid_redis_url = "redis://invalid-host:6379"

        # Mock redis.Redis.from_url to raise connection error
        with patch(
            "services.cache.cache_service.redis.Redis.from_url"
        ) as mock_from_url:
            mock_client = MagicMock()
            mock_client.ping.side_effect = Exception("Connection failed")
            mock_from_url.return_value = mock_client

            # Act & Assert
            try:
                CacheService(redis_url=invalid_redis_url)
                raise AssertionError("Should have raised CacheError")
            except CacheError as e:
                assert "Failed to connect to Redis" in str(e)

            # Verify connection attempt was made
            mock_from_url.assert_called_once_with(
                invalid_redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            mock_client.ping.assert_called_once()

    def test_set_connection_error(self, cache_service, mock_redis):
        """Test set operation with connection error."""
        # Arrange
        _, mock_client = mock_redis
        key = "test_key"
        value = "test_value"

        mock_client.set.side_effect = redis.ConnectionError("Redis connection lost")

        # Act & Assert
        with pytest.raises(CacheError, match="Failed to set key"):
            cache_service.set(key, value)

    def test_get_connection_error(self, cache_service, mock_redis):
        """Test get operation with connection error."""
        # Arrange
        _, mock_client = mock_redis
        key = "test_key"

        mock_client.get.side_effect = redis.ConnectionError("Redis connection lost")

        # Act & Assert
        with pytest.raises(CacheError, match="Failed to get key"):
            cache_service.get(key)

    def test_delete_connection_error(self, cache_service, mock_redis):
        """Test delete operation with connection error."""
        # Arrange
        _, mock_client = mock_redis
        key = "test_key"

        mock_client.delete.side_effect = redis.ConnectionError("Redis connection lost")

        # Act & Assert
        with pytest.raises(CacheError, match="Failed to delete key"):
            cache_service.delete(key)
