""" tests/test_app.py"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from observe_me.app import define_app


class TestFastAPIApp:
    """Test suite for observe_me FastAPI app."""

    @pytest.fixture
    def app(self) -> FastAPI:
        """Return a FastAPI app instance without auth."""
        return define_app(add_auth=False)

    @pytest.fixture
    def app_with_auth(self) -> FastAPI:
        """Return a FastAPI app instance with AuthMiddleware."""
        return define_app(add_auth=True)

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """Return a TestClient for the app."""
        return TestClient(app)

    @pytest.fixture
    def client_with_auth(self, app_with_auth: FastAPI) -> TestClient:
        """Return a TestClient for the app with auth."""
        return TestClient(app_with_auth)

    def test_app_instance(self, app: FastAPI) -> None:
        """Check that the returned object is a FastAPI instance."""
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)
        assert app.title == "Observer Controller"

    def test_routers_included(self, app: FastAPI) -> None:
        """Check that routers are included."""
        router_names = [r.tags[0] for r in app.router.routes if getattr(r, "tags", None)]
        assert "Router 1: API endpoints" in router_names
        assert "Router 2: Endpoints" in router_names

    # def test_cors_middleware(self, app: FastAPI) -> None:
    #     """Check that CORS middleware is added."""
    #     from fastapi.middleware.cors import CORSMiddleware
    #     middlewares = [type(mw.cls) for mw in app.user_middleware]
    #     assert CORSMiddleware in middlewares

    def test_auth_middleware_enabled(self, app_with_auth: FastAPI) -> None:
        """Check that AuthMiddleware is added when add_auth=True."""
        middlewares = [mw.cls for mw in app_with_auth.user_middleware]
        from observe_me.core import AuthMiddleware
        assert AuthMiddleware in middlewares

    def test_lifespan_runs_without_error(self) -> None:
        """Check that the lifespan context runs without errors."""
        app = define_app()
        # Use the TestClient context to run startup/shutdown
        from fastapi.testclient import TestClient
        with TestClient(app) as client:
            response = client.get("/")  # root endpoint may not exist, but lifecycle runs
            # Should return 404 because root is not defined
            assert response.status_code in [404, 200]
