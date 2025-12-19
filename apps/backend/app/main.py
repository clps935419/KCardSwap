"""KCardSwap Backend - FastAPI Application.

Main entry point for the backend service following modular DDD architecture.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .container import container
from .shared.presentation.middleware.error_handler import register_exception_handlers

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(levelname)s:%(name)s:%(message)s",
    stream=sys.stdout,
    force=True,  # Override any existing configuration
)

# Get logger for this module
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI.

    Handles startup and shutdown events.

    Note: Database tables are created by Alembic migrations.
    - In Docker: Migrations run automatically via Dockerfile entrypoint
    - In local dev: Run `poetry run alembic upgrade head` before starting the app
    """
    # Initialize container wiring (will be expanded when modules add routers)
    # container.wire() is called automatically via wiring_config in container

    yield

    # Shutdown: cleanup resources
    container.unwire()
    container.shared().db_connection_provider().close()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="KCardSwap API",
        description="Backend API for KCardSwap - Card Exchange Platform",
        version="0.1.0",
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    # Store container reference in app state
    app.container = container

    # Register exception handlers
    register_exception_handlers(app)

    # CORS middleware (Kong also handles CORS, but this provides fallback)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoints
    @app.get("/health")
    async def health_check():
        """Health check endpoint for container orchestration."""
        return {"status": "healthy", "service": "kcardswap-backend", "version": "0.1.0"}

    @app.get(f"{settings.API_PREFIX}/health")
    async def api_health_check():
        """API health check endpoint."""
        return {
            "data": {
                "status": "healthy",
                "service": "kcardswap-backend",
                "version": "0.1.0",
            },
            "error": None,
        }

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "KCardSwap API",
            "version": "0.1.0",
            "docs": f"{settings.API_PREFIX}/docs",
        }

    # Register module routers
    # Phase 3: Identity module (Authentication and Profile)
    from .modules.identity.presentation.routers.auth_router import router as auth_router
    from .modules.identity.presentation.routers.profile_router import (
        router as profile_router,
    )

    app.include_router(auth_router, prefix=settings.API_PREFIX)
    app.include_router(profile_router, prefix=settings.API_PREFIX)

    # Phase 4: Social module (Cards)
    from .modules.social.presentation.routers.cards_router import (
        router as cards_router,
    )

    app.include_router(cards_router, prefix=settings.API_PREFIX)

    # Future module routers (Phase 5+)
    # from .modules.social.presentation.routers.nearby_router import router as nearby_router
    # app.include_router(nearby_router, prefix=settings.API_PREFIX)

    return app


# Create application instance
app = create_application()
