"""Unit tests for authentication middleware validation and request flow handling."""

import unittest
from unittest.mock import AsyncMock

from observe_core.security.auth import AuthMiddleware
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response


class TestAuthMiddleware(unittest.IsolatedAsyncioTestCase):
    """Test suite for AuthMiddleware."""

    def setUp(self) -> None:
        """Create a simple mock ASGI app that returns a Response."""

        async def app(scope, receive, send):
            response = Response("OK", status_code=200)
            await response(scope, receive, send)
            return response

        self.mock_app = app

    def test_middleware_instantiation(self) -> None:
        """Test AuthMiddleware can be instantiated with default provider.

        Returns:
            None

        Asserts:
            idp_factory and idp_adapter are set correctly.
        """
        middleware = AuthMiddleware(app=self.mock_app)
        self.assertIsInstance(middleware, AuthMiddleware)
        self.assertIsNotNone(middleware.idp_factory)
        self.assertIsNotNone(middleware.idp_adapter)

    async def test_dispatch_public_path_calls_next(self) -> None:
        """Test dispatch skips authentication for public paths.

        Returns:
            None

        Asserts:
            Returns response from next ASGI app.
        """
        middleware = AuthMiddleware(app=self.mock_app)
        request = Request({"type": "http", "method": "GET", "path": "/health", "headers": {}})
        call_next = AsyncMock(return_value=Response("OK", status_code=200))
        response = await middleware.dispatch(request, call_next)
        self.assertEqual(response.status_code, 200)
        call_next.assert_awaited_once_with(request)

    async def test_validate_invalid_token_raises_http_exception(self) -> None:
        """Test validate raises HTTPException if Authorization header missing/invalid.

        Returns:
            None
        """
        middleware = AuthMiddleware(None)
        request = Request({"type": "http", "method": "GET", "path": "/secure", "headers": {}})
        with self.assertRaises(HTTPException) as exc_info:
            await middleware.validate(request)
        self.assertEqual(exc_info.exception.status_code, 401)

    async def test_validate_valid_token_sets_request_state(self) -> None:
        """Test validate stores user payload and roles in request.state for valid token.

        Returns:
            None
        """
        middleware = AuthMiddleware(None)
        # Patch adapter methods
        middleware.idp_adapter.get_payload = lambda token: {"sub": "user123"}
        middleware.idp_adapter.get_roles = lambda payload: ["admin", "user"]

        headers = {"authorization": "Bearer validtoken"}
        request = Request({
            "type": "http",
            "method": "GET",
            "path": "/secure",
            "headers": [(k.encode(), v.encode()) for k, v in headers.items()],
        })
        result_request = await middleware.validate(request)
        self.assertEqual(result_request.state.user["sub"], "user123")
        self.assertEqual(result_request.state.roles, ["admin", "user"])

    async def test_dispatch_invalid_token_returns_401(self) -> None:
        """Test dispatch returns 401 JSONResponse when token invalid.

        Returns:
            None
        """
        middleware = AuthMiddleware(None)
        call_next = AsyncMock()
        request = Request({"type": "http", "method": "GET", "path": "/secure", "headers": {}})
        response = await middleware.dispatch(request, call_next)
        self.assertEqual(response.status_code, 401)
