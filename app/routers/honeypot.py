from fastapi import APIRouter, Request, HTTPException, status

router = APIRouter()

# Note: The actual logging and blocking is handled by the middleware.
# These endpoints just return generic deceptive responses if reached.

@router.get("/admin/config")
async def get_admin_config():
    # Return a deceptive generic error
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

@router.post("/v1/auth/login")
async def fake_login():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@router.get("/wp-admin")
async def get_wp_admin():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

@router.get("/.env")
async def get_env():
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

# Catch-all for any other path that isn't explicitly defined
@router.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def catch_all(request: Request, path_name: str):
    # This ensures that even if they hit a random endpoint we don't have,
    # the middleware still catches it, logs it, and they get a generic 404 here.
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
