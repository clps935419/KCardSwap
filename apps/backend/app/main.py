"""
KCardSwap Backend - FastAPI Application
Main entry point for the backend service.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="KCardSwap API",
    description="Backend API for KCardSwap - Card Exchange Platform",
    version="0.1.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS middleware (Kong also handles CORS, but this provides fallback)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
