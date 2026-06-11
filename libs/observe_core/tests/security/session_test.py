"""Unit tests for session middleware context propagation and header injection."""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, Awaitable, Callable, Dict, List
from uuid import UUID

from opentelemetry import context as otel_context
from starlette.types import Receive, Scope, Send

# Assuming the file is named session.py and dependencies are structured correctly
from observe_core.security import SessionMiddleware
from observe_core.context import get_context, _context_var
from observe_core.headers import HEADER_BEDROCK_ACTOR_ID, HEADER_BEDROCK_SESSION_ID


class TestSessionMiddleware(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the SessionMiddleware ASGI component."""

    def setUp(self) -> None:
        """Reset the internal ObserveContext ContextVar before each execution."""
        self.token = _context_var.set(None)
        # Create a generic mock ASGI application to pass down the chain
        self.mock_app = AsyncMock()

    def tearDown(self) -> None:
        """Clean up the ContextVar after test completion."""
        _context_var.reset(self.token)

    def _create_asgi_arguments(
            self, scope_type: str = "http", headers: List[tuple[bytes, bytes]] = None
    ) -> tuple[Scope, Receive, Send]:
        """Helper to generate standard mock ASGI Scope, Receive, and Send arguments."""
        scope: Scope = {
            "type": scope_type,
            "headers": headers or [],
        }
        receive: Receive = AsyncMock()
        send: Send = AsyncMock()
        return scope, receive, send

    async def test_passthrough_non_http_or_websocket_scopes(self) -> None:
        """Test that lifespan or other system ASGI events pass through unmodified."""
        middleware = SessionMiddleware(self.mock_app)
        scope: Scope = {"type": "lifespan"}
        receive: Receive = AsyncMock()
        send: Send = AsyncMock()

        await middleware(scope, receive, send)

        # The underlying app should be called directly with the exact untouched arguments
        self.mock_app.assert_called_once_with(scope, receive, send)
        self.assertIsNone(get_context())

    @patch("observe_core.security.session.trace.get_current_span")
    @patch("observe_core.security.session.otel_baggage.set_baggage")
    async def test_handle_http_with_incoming_headers(
            self, mock_set_baggage: MagicMock, mock_get_current_span: MagicMock
    ) -> None:
        """Test successful session extraction, OTEL tracking, and header propagation from valid HTTP headers."""
        # Mock OpenTelemetry Span interactions
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_get_current_span.return_value = mock_span

        # Define headers using lowercase or official names (Middleware decodes them)
        incoming_headers: List[tuple[bytes, bytes]] = [
            (HEADER_BEDROCK_ACTOR_ID.lower().encode(), b"actor_abc"),
            (HEADER_BEDROCK_SESSION_ID.lower().encode(), b"session_123"),
        ]
        scope, receive, send = self._create_asgi_arguments("http", incoming_headers)
        middleware = SessionMiddleware(self.mock_app, local_dev=False)

        # Execute middleware
        await middleware(scope, receive, send)

        # 1. Check internal context propagation
        current_context = get_context()
        self.assertIsNotNone(current_context)
        self.assertEqual(current_context.actor_id, "actor_abc")  # type: ignore
        self.assertEqual(current_context.session_id, "session_123")  # type: ignore

        # 2. Check OpenTelemetry telemetry attachments
        mock_set_baggage.assert_called_once_with("session.id", "session_123")
        mock_span.set_attribute.assert_called_once_with("agentcore.session_id", "session_123")

        # 3. Verify downstream app execution
        self.mock_app.assert_called_once()

    async def test_session_generation_in_local_development(self) -> None:
        """Test that missing session IDs are auto-generated as UUIDs when local_dev is active."""
        scope, receive, send = self._create_asgi_arguments("http", headers=[])

        # Enable local development
        middleware = SessionMiddleware(self.mock_app, local_dev=True)
        await middleware(scope, receive, send)

        current_context = get_context()
        self.assertIsNotNone(current_context)
        # Assert it's a valid generated UUID string
        self.assertIsNotNone(current_context.session_id)  # type: ignore
        try:
            UUID(current_context.session_id)  # type: ignore
        except ValueError:
            self.fail("session_id is not a valid UUID string")

    async def test_no_session_generation_in_production(self) -> None:
        """Test that missing session IDs remain None if local_dev is turned off (Production behavior)."""
        scope, receive, send = self._create_asgi_arguments("http", headers=[])

        # Disabled local dev
        middleware = SessionMiddleware(self.mock_app, local_dev=False)
        await middleware(scope, receive, send)

        current_context = get_context()
        self.assertIsNotNone(current_context)
        self.assertIsNone(current_context.session_id)  # type: ignore

    async def test_session_id_extraction_from_baggage_header(self) -> None:
        """Test fallback extraction of session.id out of standard W3C baggage string headers."""
        incoming_headers: List[tuple[bytes, bytes]] = [
            (b"baggage", b"other_param=foo,session.id=baggage_sess_999,key=val")
        ]
        scope, receive, send = self._create_asgi_arguments("http", incoming_headers)
        middleware = SessionMiddleware(self.mock_app, local_dev=False)

        await middleware(scope, receive, send)

        current_context = get_context()
        self.assertEqual(current_context.session_id, "baggage_sess_999")  # type: ignore

    async def test_corrupted_baggage_header_graceful_handling(self) -> None:
        """Test that a corrupted or malformed baggage string does not crash the server lifecycle."""
        incoming_headers: List[tuple[bytes, bytes]] = [
            (b"baggage", b"invalid_malformed_string_without_equals_signs")
        ]
        scope, receive, send = self._create_asgi_arguments("http", incoming_headers)
        middleware = SessionMiddleware(self.mock_app, local_dev=False)

        # Should execute smoothly without crashing out with ValueError
        await middleware(scope, receive, send)
        current_context = get_context()
        self.assertIsNone(current_context.session_id)  # type: ignore

    async def test_websocket_skips_response_header_injection(self) -> None:
        """Test that WebSockets execute without wrapping the send function with header injection configs."""
        scope, receive, send = self._create_asgi_arguments("websocket", [])
        middleware = SessionMiddleware(self.mock_app, local_dev=False)

        await middleware(scope, receive, send)

        # WebSocket doesn't call _handle_http; checks if app received standard untouched send
        self.mock_app.assert_called_once_with(scope, receive, send)

    async def test_http_response_header_injection_intercept(self) -> None:
        """Test that HTTP response headers intercept the outbound stream to append tracking info."""
        incoming_headers: List[tuple[bytes, bytes]] = [
            (HEADER_BEDROCK_ACTOR_ID.lower().encode(), b"actor_xyz"),
            (HEADER_BEDROCK_SESSION_ID.lower().encode(), b"session_xyz"),
        ]
        scope, receive, send = self._create_asgi_arguments("http", incoming_headers)
        middleware = SessionMiddleware(self.mock_app, local_dev=False)

        # Trigger middleware execution
        await middleware(scope, receive, send)

        # Capture the modified 'send_with_headers' function passed downstream
        called_args, _ = self.mock_app.call_args
        intercepted_send: Send = called_args[2]

        # Simulate a mock outbound ASGI payload from the router
        mock_response_message: Dict[str, Any] = {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"application/json")],
        }

        # Fire the intercepted send wrapper
        await intercepted_send(mock_response_message)

        # Extract arguments sent back to the primary ASGI pipeline server
        send.assert_called_once()
        modified_message = send.call_args[0][0]

        # Convert outbound list of tuples back to dict for validation checks
        outbound_headers = dict(modified_message["headers"])

        self.assertEqual(outbound_headers[HEADER_BEDROCK_ACTOR_ID.lower().encode()], b"actor_xyz")
        self.assertEqual(outbound_headers[HEADER_BEDROCK_SESSION_ID.lower().encode()], b"session_xyz")
        self.assertEqual(outbound_headers[b"content-type"], b"application/json")


if __name__ == "__main__":
    unittest.main()
