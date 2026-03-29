# tests/test_auth_middleware.py
from unittest.mock import AsyncMock

import pytest
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from observe_me.core.security.auth import AuthMiddleware


@pytest.mark.asyncio
class TestAuthMiddleware:
    """Test suite for AuthMiddleware."""

    @pytest.fixture
    def mock_app(self):
        """Return a simple mock ASGI app that returns a Response."""

        async def app(scope, receive, send):
            response = Response("OK", status_code=200)
            await response(scope, receive, send)
            return response

        return app

    def test_middleware_instantiation(self, mock_app):
        """Test AuthMiddleware can be instantiated with default provider.

        Returns:
            None

        Asserts:
            idp_factory and idp_adapter are set correctly.
        """
        middleware = AuthMiddleware(app=mock_app)
        assert isinstance(middleware, AuthMiddleware)
        assert middleware.idp_factory is not None
        assert middleware.idp_adapter is not None

    @pytest.mark.asyncio
    async def test_dispatch_public_path_calls_next(self, mock_app):
        """Test dispatch skips authentication for public paths.

        Returns:
            None

        Asserts:
            Returns response from next ASGI app.
        """
        middleware = AuthMiddleware(app=mock_app)
        request = Request({"type": "http", "method": "GET", "path": "/health", "headers": {}})
        call_next = AsyncMock(return_value=Response("OK", status_code=200))
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200
        call_next.assert_awaited_once_with(request)

    @pytest.mark.asyncio
    async def test_validate_invalid_token_raises_http_exception(self):
        """Test validate raises HTTPException if Authorization header missing/invalid.

        Returns:
            None
        """
        middleware = AuthMiddleware()
        request = Request({"type": "http", "method": "GET", "path": "/secure", "headers": {}})
        with pytest.raises(HTTPException) as exc_info:
            await middleware.validate(request)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_validate_valid_token_sets_request_state(self):
        """Test validate stores user payload and roles in request.state for valid token.

        Returns:
            None
        """
        middleware = AuthMiddleware()
        # Patch adapter methods
        middleware.idp_adapter.get_payload = lambda token: {"sub": "user123"}
        middleware.idp_adapter.get_roles = lambda payload: ["admin", "user"]

        headers = {"authorization": "Bearer validtoken"}
        request = Request({"type": "http", "method": "GET", "path": "/secure",
                           "headers": [(k.encode(), v.encode()) for k, v in headers.items()]})
        result_request = await middleware.validate(request)
        assert result_request.state.user["sub"] == "user123"
        assert result_request.state.roles == ["admin", "user"]

    @pytest.mark.asyncio
    async def test_dispatch_invalid_token_returns_401(self):
        """Test dispatch returns 401 JSONResponse when token invalid.

        Returns:
            None
        """
        middleware = AuthMiddleware()
        call_next = AsyncMock()
        request = Request({"type": "http", "method": "GET", "path": "/secure", "headers": {}})
        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 401
