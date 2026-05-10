import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-Admin-Token", auto_error=False)

async def verify_admin_token(api_key_header: str = Security(api_key_header)):
    # Default fallback token if not configured, though it should be
    expected_token = os.getenv("ADMIN_API_KEY", "super-secret-admin-token-change-me")
    
    if api_key_header == expected_token:
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
    )
