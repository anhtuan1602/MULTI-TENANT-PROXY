import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from proxy_server import app
from services.redis_tracker import redis_client

@pytest.fixture(autouse=True)
def clear_redis():
    """Clears the simulated Redis database before every single test run."""
    redis_client.flushdb()

@pytest.mark.asyncio
async def test_free_tier_rate_limiting():
    """
    Tests that a Free Tier user (limit: 3) can successfully make 3 requests,
    but the 4th request is instantly blocked with an HTTP 429 status code.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = {"X-API-Key": "free_tier_key"}
        
        # First 3 requests should fly through smoothly
        for i in range(3):
            response = await ac.get("/api/resource", headers=headers)
            assert response.status_code == 200
            assert response.json()["status"] == "Success"
            
        # The 4th concurrent request must trigger the limit
        blocked_response = await ac.get("/api/resource", headers=headers)
        assert blocked_response.status_code == 429
        assert "Retry-After" in blocked_response.headers
        assert int(blocked_response.headers["Retry-After"]) > 0
        print(f"\n\n✅ Free tier successfully throttled! Header response: {blocked_response.headers}")

@pytest.mark.asyncio
async def test_premium_tier_higher_allowance():
    """Tests that a Premium Tier user can make more requests than a free tier user."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = {"X-API-Key": "premium_tier_key"}
        
        # Premium can easily handle 7 requests without breaking a sweat
        for i in range(7):
            response = await ac.get("/api/resource", headers=headers)
            assert response.status_code == 200
            
        print(f"\n✅ Premium user successfully completed 7 continuous requests.")
