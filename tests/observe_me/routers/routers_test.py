"""tests/test_v1_router.py"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from observe_me.config import __version__
from observe_me.routers.routes import v1_router


class TestV1Router:
    """Test suite for observe_me.v1_router endpoints."""

    @pytest.fixture
    def app(self) -> FastAPI:
        """Return a FastAPI app instance with v1_router included.

        Returns:
            FastAPI: App instance with v1_router mounted.
        """
        app = FastAPI()
        app.include_router(v1_router)
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

    def test_route_status_code(self, client: TestClient):
        """Test that /route endpoint returns HTTP 200 status.

        Args:
            client (TestClient): Test client for FastAPI app.

        Returns:
            None

        Asserts:
            Response status code is 200.
        """
        response = client.get("/route", params={"name": "Alice"})
        assert response.status_code == 200

    # def test_route_response_type(self, client: TestClient):
    #     """Test that /route endpoint returns a JSONResponse.
    #
    #     Args:
    #         client (TestClient): Test client for FastAPI app.
    #
    #     Returns:
    #         None
    #
    #     Asserts:
    #         Response is instance of JSONResponse.
    #     """
    #     response = client.get("/route", params={"name": "Alice"})
    #     assert isinstance(response, JSONResponse)

    def test_route_response_content(self, client: TestClient):
        """Test that /route endpoint returns the correct JSON content with version.

        Args:
            client (TestClient): Test client for FastAPI app.

        Returns:
            None

        Asserts:
            JSON response contains a key with the name parameter and version.
        """
        name = "Alice"
        response = client.get("/route", params={"name": name})
        data = response.json()
        expected_key = f"{name}, the version is"
        assert expected_key in data
        assert data[expected_key] == __version__
