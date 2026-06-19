"""HTTP endpoint tests for the API health router and version payload contract."""

import unittest

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from observe_api.config import __version__
from observe_api.routers import api_router


class TestAPIRouter(unittest.TestCase):
    """Test suite for observe_api.api_router endpoints."""

    @pytest.fixture
    def app(self) -> FastAPI:
        """Return a FastAPI app instance with api_router included.

        Returns:
            FastAPI: App instance with api_router mounted.
        """
        app = FastAPI()
        app.include_router(api_router)
        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """Return a TestClient for the FastAPI app.

        Args:
            app (FastAPI): The FastAPI instance to test.

        Returns:
            TestClient: Client for making HTTP requests to the app.
        """
        return TestClient(app)

    def test_health_endpoint_status(self, client: TestClient) -> None:
        """Test that /health endpoint returns HTTP 200 status.

        Args:
            client (TestClient): Test client for FastAPI app.

        Asserts:
            Status code is 200.
        """
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)

    # def test_health_endpoint_response_type(self, client: TestClient):
    #     """Test that /health endpoint returns a JSONResponse.
    #
    #     Args:
    #         client (TestClient): Test client for FastAPI app.
    #
    #     Asserts:
    #         Response is instance of JSONResponse.
    #     """
    #     response = client.get("/health")
    #     assert isinstance(response, JSONResponse)

    def test_health_endpoint_content(self, client: TestClient) -> None:
        """Test that /health endpoint returns correct version in JSON content.

        Args:
            client (TestClient): Test client for FastAPI app.

        Asserts:
            JSON response contains 'version' matching __version__.
        """
        response = client.get("/health")
        data = response.json()
        self.assertIn("version", data)
        self.assertEqual(data["version"], __version__)
