from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.database import init_db
from app.api import router
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title="OPD Token Allocation Engine",
    description="""
    A sophisticated token allocation system for hospital OPD with elastic capacity management.
    
    ## Features
    
    * **Dynamic Token Allocation**: Intelligently allocate tokens based on priority
    * **Multi-Source Support**: Handle online bookings, walk-ins, priority patients, and follow-ups
    * **Capacity Management**: Enforce per-slot hard limits with overflow handling
    * **Real-time Reallocation**: Handle delays, cancellations, and emergency insertions
    * **Queue Management**: Priority-based patient queuing
    * **Analytics**: Comprehensive insights into OPD operations
    
    ## Token Sources (Priority Order)
    
    1. **Priority Patients** (Paid/VIP) - Highest priority
    2. **Follow-up Patients** - Medium-high priority
    3. **Online Booking** - Medium priority
    4. **Walk-in** - Standard priority
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )


# Include API router
app.include_router(router, prefix="/api/v1", tags=["OPD Token System"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "OPD Token Allocation Engine",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )
