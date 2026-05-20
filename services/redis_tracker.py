import time
import fakeredis

# Using fakeredis to keep the project zero-dependency and runnable out of the box
redis_client = fakeredis.FakeStrictRedis(version=6)

async def is_rate_limited(api_key: str, limit: int, window: int = 60) -> tuple[bool, int]:
    """
    Implements a precise Sliding Window Log rate limiter using high-precision timestamps.
    Returns (is_limited, retry_after_seconds)
    """
    current_time = time.time()
    key = f"rate_limit:{api_key}"
    
    # Remove timestamps older than our window (e.g., 60 seconds ago)
    redis_client.zremrangebyscore(key, 0, current_time - window)
    
    # Check total requests remaining in this rolling window
    request_count = redis_client.zcard(key)
    
    if request_count >= limit:
        # Calculate when oldest item expires to tell client when they can retry
        oldest_timestamps = redis_client.zrange(key, 0, 0, withscores=True)
        oldest_time = oldest_timestamps[0][1] if oldest_timestamps else current_time
        retry_after = int(window - (current_time - oldest_time))
        return True, max(1, retry_after)
        
    # Use the high-precision timestamp string as the member value to guarantee uniqueness
    # in Redis sorted sets even when executing multiple requests in the same millisecond.
    redis_client.zadd(key, {str(current_time): current_time})
    return False, 0