# config.py

TENANT_LIMITS = {
    "free_tier_key": {
        "name": "Regular Customer",
        "tier": "Free",
        "rate_limit": 3,
        "window": 60
    },
    "premium_tier_key": {
        "name": "VIP Customer",
        "tier": "Premium",
        "rate_limit": 10,
        "window": 60
    }
}