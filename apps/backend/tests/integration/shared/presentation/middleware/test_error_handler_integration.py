"""
Integration tests for Error Handler Middleware

Tests error handling middleware with real FastAPI app.
"""

import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.shared.presentation.exceptions.api_exceptions import APIError
from app.shared.presentation.middleware.error_handler import (
    api_exception_handler,
    general_exception_handler,
    http_exception_handler,
    register_exception_handlers,
    validation_exception_handler,
)


class TestErrorHandlerMiddlewareIntegration:
    """Integration tests for error handler middleware"""

    @pytest.fixture
    def test_app(self):
        """Create test FastAPI app with error handlers"""
        app = FastAPI()
        register_exception_handlers(app)
        
        @app.get("/test-api-error")
        async def test_api_error():
            raise APIError(
                status_code=404,
                error_code="404_NOT_FOUND",
                message="Resource not found",
                details={"resource_id": "123"}
            )
        
        @app.get("/test-http-error")
        async def test_http_error():
            raise HTTPException(status_code=403, detail="Forbidden")
        
        @app.get("/test-validation-error")
        async def test_validation_error(value: int):
            return {"value": value}
        
        @app.get("/test-general-error")
        async def test_general_error():
            raise ValueError("Unexpected error")
        
        return app

    def test_api_exception_handler_integration(self, test_app):
        """Test API exception handler returns correct format"""
        # Arrange
        client = TestClient(test_app, raise_server_exceptions=False)

        # Act
        response = client.get("/test-api-error")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["data"] is None
        assert data["meta"] is None
        assert data["error"]["code"] == "404_NOT_FOUND"
        assert data["error"]["message"] == "Resource not found"
        assert data["error"]["details"]["resource_id"] == "123"

    def test_http_exception_handler_integration(self, test_app):
        """Test HTTP exception handler returns correct format"""
        # Arrange
        client = TestClient(test_app, raise_server_exceptions=False)

        # Act
        response = client.get("/test-http-error")

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert data["data"] is None
        assert data["meta"] is None
        assert data["error"]["code"] == "403_HTTP_ERROR"
        assert data["error"]["message"] == "Forbidden"

    def test_validation_exception_handler_integration(self, test_app):
        """Test validation exception handler returns correct format"""
        # Arrange
        client = TestClient(test_app, raise_server_exceptions=False)

        # Act - Send invalid data type
        response = client.get("/test-validation-error?value=invalid")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["data"] is None
        assert data["meta"] is None
        assert data["error"]["code"] == "400_VALIDATION_FAILED"
        assert data["error"]["message"] == "Request validation failed"
        assert "errors" in data["error"]["details"]
        assert len(data["error"]["details"]["errors"]) > 0

    def test_general_exception_handler_integration(self, test_app):
        """Test general exception handler returns correct format"""
        # Arrange
        client = TestClient(test_app, raise_server_exceptions=False)

        # Act
        response = client.get("/test-general-error")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert data["data"] is None
        assert data["meta"] is None
        assert data["error"]["code"] == "500_INTERNAL_ERROR"
        assert data["error"]["message"] == "An unexpected error occurred"

    def test_multiple_validation_errors(self, test_app):
        """Test validation with multiple field errors"""
        # Arrange
        app = FastAPI()
        register_exception_handlers(app)
        
        class TestModel(BaseModel):
            email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
            age: int = Field(..., gt=0, lt=150)
        
        @app.post("/test-multi-validation")
        async def test_endpoint(data: TestModel):
            return data
        
        client = TestClient(app, raise_server_exceptions=False)

        # Act - Send data with multiple validation errors
        response = client.post(
            "/test-multi-validation",
            json={"email": "invalid-email", "age": -5}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "400_VALIDATION_FAILED"
        assert "errors" in data["error"]["details"]

    def test_missing_required_fields(self, test_app):
        """Test validation with missing required fields"""
        # Arrange
        app = FastAPI()
        register_exception_handlers(app)
        
        class RequiredModel(BaseModel):
            name: str
            email: str
        
        @app.post("/test-required")
        async def test_endpoint(data: RequiredModel):
            return data
        
        client = TestClient(app, raise_server_exceptions=False)

        # Act - Send incomplete data
        response = client.post("/test-required", json={"name": "John"})

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "400_VALIDATION_FAILED"

    def test_error_handler_with_different_status_codes(self, test_app):
        """Test error handlers with various HTTP status codes"""
        # Arrange
        app = FastAPI()
        register_exception_handlers(app)
        
        @app.get("/test-401")
        async def test_401():
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        @app.get("/test-500")
        async def test_500():
            raise Exception("Internal error")
        
        client = TestClient(app, raise_server_exceptions=False)

        # Act & Assert
        response_401 = client.get("/test-401")
        assert response_401.status_code == 401
        assert response_401.json()["error"]["code"] == "401_HTTP_ERROR"

        response_500 = client.get("/test-500")
        assert response_500.status_code == 500
        assert response_500.json()["error"]["code"] == "500_INTERNAL_ERROR"

    def test_api_error_with_empty_details(self, test_app):
        """Test API error with no details"""
        # Arrange
        app = FastAPI()
        register_exception_handlers(app)
        
        @app.get("/test-no-details")
        async def test_endpoint():
            raise APIError(
                status_code=400,
                error_code="400_BAD_REQUEST",
                message="Bad request",
                details={}
            )
        
        client = TestClient(app, raise_server_exceptions=False)

        # Act
        response = client.get("/test-no-details")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["details"] == {}
