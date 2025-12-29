"""KCardSwap Backend - FastAPI Application.

Main entry point for the backend service following modular DDD architecture.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .injector import injector
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
    # Injector is already initialized in app/injector.py
    # No wiring needed with python-injector

    yield

    # Shutdown: cleanup resources
    from .shared.infrastructure.database.connection import db_connection

    db_connection.close()


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

    # Store injector reference in app state
    app.state.injector = injector

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

    # Phase 5: Social module (Nearby Search)
    from .modules.social.presentation.routers.nearby_router import (
        router as nearby_router,
    )

    app.include_router(nearby_router, prefix=settings.API_PREFIX)

    # Phase 6: Social module (Friends, Chat, Ratings, Reports)
    from .modules.social.presentation.routers.chat_router import router as chat_router
    from .modules.social.presentation.routers.friends_router import (
        router as friends_router,
    )
    from .modules.social.presentation.routers.rating_router import (
        router as rating_router,
    )
    from .modules.social.presentation.routers.report_router import (
        router as report_router,
    )

    app.include_router(friends_router, prefix=settings.API_PREFIX)
    app.include_router(chat_router, prefix=settings.API_PREFIX)
    app.include_router(rating_router, prefix=settings.API_PREFIX)
    app.include_router(report_router, prefix=settings.API_PREFIX)

    # Phase 7: Social module (Trade)
    from .modules.social.presentation.routers.trade_router import (
        router as trade_router,
    )

    app.include_router(trade_router, prefix=settings.API_PREFIX)

    # Phase 8: Identity module (Subscription)
    from .modules.identity.presentation.routers.subscription_router import (
        router as subscription_router,
    )

    app.include_router(subscription_router, prefix=settings.API_PREFIX)

    # Phase 8.5: Posts module (City Board Posts)
    from .modules.posts.presentation.routers.posts_router import (
        router as posts_router,
    )

    app.include_router(posts_router, prefix=settings.API_PREFIX)

    return app


# Create application instance
app = create_application()
