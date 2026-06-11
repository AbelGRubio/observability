"""Integration-style tests for FastAPI application assembly and middleware wiring."""

import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from observe_api.app import define_app


class TestFastAPIApp(unittest.TestCase):
    """Test suite for observe_api FastAPI app."""

    def setUp(self) -> None:
        """Create app instances and clients for each test."""
        self.app: FastAPI = define_app(add_auth=False)
        self.app_with_auth: FastAPI = define_app(add_auth=True)
        self.client: TestClient = TestClient(self.app)
        self.client_with_auth: TestClient = TestClient(self.app_with_auth)

    def test_app_instance(self) -> None:
        """Check that the returned object is a FastAPI instance."""
        from fastapi import FastAPI

        self.assertIsInstance(self.app, FastAPI)
        self.assertEqual(self.app.title, "Observer Controller")

    def test_routers_included(self) -> None:
        """Check that routers are included."""
        router_names = [r.tags[0] for r in self.app.router.routes if getattr(r, "tags", None)]
        self.assertIn("Router 1: API endpoints", router_names)
        self.assertIn("Router 2: Endpoints", router_names)

    # def test_cors_middleware(self, app: FastAPI) -> None:
    #     """Check that CORS middleware is added."""
    #     from fastapi.middleware.cors import CORSMiddleware
    #     middlewares = [type(mw.cls) for mw in app.user_middleware]
    #     assert CORSMiddleware in middlewares

    def test_auth_middleware_enabled(self) -> None:
        """Check that AuthMiddleware is added when add_auth=True."""
        middlewares = [mw.cls for mw in self.app_with_auth.user_middleware]
        from observe_core import AuthMiddleware

        self.assertIn(AuthMiddleware, middlewares)

    def test_lifespan_runs_without_error(self) -> None:
        """Check that the lifespan context runs without errors."""
        app = define_app()
        # Use the TestClient context to run startup/shutdown
        from fastapi.testclient import TestClient

        with TestClient(app) as client:
            response = client.get("/")  # root endpoint may not exist, but lifecycle runs
            # Should return 404 because root is not defined
            self.assertIn(response.status_code, [404, 200])
