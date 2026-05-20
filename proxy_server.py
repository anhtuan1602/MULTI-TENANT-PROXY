
from fastapi import FastAPI, Header, HTTPException, Response
from config import TIER_LIMITS
from services.redis_tracker import is_rate_limited

app = FastAPI(title="Multi-Tenant Rate Limiting Proxy Gateway")

@app.get("/status")
async def status(response: Response):
    response.headers["Cache-Control"] = "no-store"
    return {"status": "ok", "service": "Multi-Tenant Rate Limiting Proxy Gateway"}

@app.get("/api/resource")
async def gateway(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key not in TIER_LIMITS:
        raise HTTPException(status_code=401, detail="Invalid or Missing API Key Header.")
        
    tier = TIER_LIMITS[x_api_key]
    limited, retry_after = await is_rate_limited(x_api_key, tier["limit"])
    
    if limited:
        return Response(
            content=f"Rate Limit Exceeded for {tier['name']}. Upgrade tier or try later.",
            status_code=429,
            headers={"Retry-After": str(retry_after)}
        )
        
    return {
        "status": "Success",
        "tenant": tier["name"],
        "message": "Traffic forwarded successfully to downstream backend layer."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
