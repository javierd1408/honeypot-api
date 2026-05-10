import json
from fastapi import Request, BackgroundTasks
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.security.threat_classifier import classify_threat
from app.security.rate_limiter import record_request
from app.database import AsyncSessionLocal
from app.models import IntrusionLog

async def save_intrusion_log(log_data: dict):
    """
    Background task to save the intrusion log to the database asynchronously.
    """
    async with AsyncSessionLocal() as session:
        new_log = IntrusionLog(**log_data)
        session.add(new_log)
        await session.commit()

class HoneypotMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Skip middleware for our internal protected dashboard API
        if request.url.path.startswith("/api/v1/intruders"):
            return await call_next(request)

        # 2. Get IP Address
        client_ip = request.client.host if request.client else "Unknown"

        # 3. Check Rate Limit (Drop the request if blocked)
        # We return a generic 429 without giving hints it's a security ban
        if record_request(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"}
            )

        # 4. Extract Request Data
        headers = dict(request.headers)
        user_agent = headers.get("user-agent", "Unknown")
        method = request.method
        path = request.url.path
        
        # Read payload safely (we need to restore it so the router could potentially read it, 
        # though in our honeypot we mostly drop it, but it's good practice).
        # Since we use BaseHTTPMiddleware, reading body can be tricky as it consumes the stream.
        # For a pure honeypot where we don't care about the downstream reading the body, 
        # we can read it directly.
        body_bytes = await request.body()
        payload = body_bytes.decode('utf-8', errors='ignore') if body_bytes else None

        # 5. Classify Threat
        threat_type = classify_threat(path=path, method=method, payload=payload)

        # 6. Prepare data for database
        log_data = {
            "ip_address": client_ip,
            "user_agent": user_agent,
            "headers": headers, # Store as JSON
            "payload": payload,
            "endpoint": path,
            "method": method,
            "threat_type": threat_type
        }

        # 7. Add the save task to BackgroundTasks
        # BaseHTTPMiddleware doesn't have direct access to FastAPI's BackgroundTasks injected into routes.
        # We handle it by passing the task to a background thread/task runner or using a simple asyncio.create_task 
        # for true "fire and forget" if we are outside of a standard route context.
        # However, a cleaner way in Starlette middleware is to inject it into the request state and let a generic 
        # route handle it, OR we just await it (which blocks slightly). 
        # To truly make it background from middleware, we can use request.app.state or asyncio.create_task.
        import asyncio
        asyncio.create_task(save_intrusion_log(log_data))

        # 8. Proceed to the actual router (which will mostly return generic 404s/401s)
        response = await call_next(request)
        return response
