"""Dependency injection utilities for FastAPI endpoints."""

from fastapi import Request
from injector import Injector


def get_injector(request: Request) -> Injector:
    """Get the injector instance from the app state."""
    return request.app.state.injector
