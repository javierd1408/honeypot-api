from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import honeypot, dashboard
from app.middleware.logging_middleware import HoneypotMiddleware
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI startup and shutdown.
    Handles DB initialization.
    """
    logger.info("Initializing database...")
    async with engine.begin() as conn:
        # For an educational project, we create tables on startup.
        # In production, use Alembic migrations instead.
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized.")
    
    yield
    
    logger.info("Shutting down...")
    await engine.dispose()

app = FastAPI(
    title="Internal Configuration API", 
    description="System endpoints.",
    version="1.0.0",
    docs_url=None, # Disable Swagger UI to look less like a FastAPI app to basic scanners
    redoc_url=None, # Disable ReDoc
    lifespan=lifespan
)

# Add our custom security and logging middleware
app.add_middleware(HoneypotMiddleware)

# Include routers
# We prefix the dashboard so it's separated from the honeypot routes
app.include_router(dashboard.router, prefix="/api/v1")

# The honeypot router has no prefix because it handles root-level deceptive endpoints
# AND it acts as a catch-all. Therefore, it MUST be included last.
app.include_router(honeypot.router)

