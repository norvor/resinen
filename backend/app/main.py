from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import redis_client

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- 1. MIDDLEWARE (CORS) ---
# Allow the SvelteKit frontend to talk to this API
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- 2. ROUTERS ---
# We group all v1 endpoints (users, auth, social) in a single router
app.include_router(api_router, prefix=settings.API_V1_STR)

# --- 3. HEALTH CHECK ---
@app.get("/health")
def health_check():
    """
    Simple probe for AWS/K8s/Docker to check if we are alive.
    Also checks Redis connection.
    """
    redis_status = "offline"
    try:
        if redis_client.ping():
            redis_status = "online"
    except Exception:
        pass
        
    return {
        "status": "ok", 
        "version": "0.1.0",
        "redis": redis_status
    }

# --- 4. STARTUP EVENTS ---
@app.on_event("startup")
async def startup_event():
    print(f"🚀 {settings.PROJECT_NAME} Backend Started")
    print(f"📡 API accessible at http://localhost:8000{settings.API_V1_STR}")
    try:
        if redis_client.ping():
            print("✅ Redis Cache Connected")
    except Exception as e:
        print(f"⚠️ Redis Connection Failed: {e}")