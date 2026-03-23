"""Tests for the FastAPI application endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["app"] == "AI Wrapper"
        assert "version" in data

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestCORS:
    def test_cors_headers(self):
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200


class TestAPIRoutes:
    def test_docs_available(self):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_available(self):
        response = client.get("/redoc")
        assert response.status_code == 200
