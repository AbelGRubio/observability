"""HTTP endpoint tests for the v1 router route response status and payload format."""

import unittest

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from observe_api.config import __version__
from observe_api.routers.routes import v1_router


class TestV1Router(unittest.TestCase):
    """Test suite for observe_api.v1_router endpoints."""

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

    def test_route_status_code(self, client: TestClient) -> None:
        """Test that /route endpoint returns HTTP 200 status.

        Args:
            client (TestClient): Test client for FastAPI app.

        Returns:
            None

        Asserts:
            Response status code is 200.
        """
        response = client.get("/route", params={"name": "Alice"})
        self.assertEqual(response.status_code, 200)

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

    def test_route_response_content(self, client: TestClient) -> None:
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
        self.assertEqual(expected_key, data)
        self.assertEqual(data[expected_key], __version__)
