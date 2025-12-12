"""
KCardSwap Backend - FastAPI Application
Main entry point for the backend service.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .infrastructure.database import init_db
from .presentation.routers import auth_router, profile_router
from .container import Container


# Initialize IoC Container
container = Container()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI
    Handles startup and shutdown events
    """
    # Startup: Initialize database and wire container
    await init_db()
    
    # Wire container for dependency injection
    container.wire(modules=[
        "app.presentation.routers.auth_router",
        "app.presentation.routers.profile_router",
        "app.presentation.dependencies.auth_dependencies",
        "app.presentation.dependencies.ioc_dependencies"
    ])
    
    yield
    
    # Shutdown: cleanup
    container.unwire()


app = FastAPI(
    title="KCardSwap API",
    description="Backend API for KCardSwap - Card Exchange Platform",
    version="0.1.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# Store container reference in app state for access in routes
app.container = container

# CORS middleware (Kong also handles CORS, but this provides fallback)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router.router)
app.include_router(profile_router.router)


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "service": "kcardswap-backend",
        "version": "0.1.0"
    }


@app.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "data": {
            "status": "healthy",
            "service": "kcardswap-backend",
            "version": "0.1.0"
        },
        "error": None
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "KCardSwap API",
        "version": "0.1.0",
        "docs": "/api/v1/docs"
    }
