"""Session middleware for FastAPI with OpenTelemetry context propagation.

Provides session ID extraction and attachment to OTEL baggage and span
attributes, ensuring trace correlation across services and async tasks.
Supports both HTTP and WebSocket connections.
"""

import logging
from typing import Any
from uuid import uuid4

from opentelemetry import baggage as otel_baggage
from opentelemetry import context, trace
from starlette.types import ASGIApp, Receive, Scope, Send

from observe_core.context import ObserveContext, set_context
from observe_core.headers import HEADER_BEDROCK_ACTOR_ID, HEADER_BEDROCK_SESSION_ID, ObserveHeaders

logger = logging.getLogger(__name__)


class SessionMiddleware:
    """ASGI middleware to handle session propagation and observability.

    Handles both HTTP requests and WebSocket connections, ensuring trace
    correlation and context propagation across downstream services or async tasks.
    """

    def __init__(self, app: ASGIApp, local_dev: bool = False) -> None:
        """Constructor for middleware."""
        self.app = app
        self.local_dev = local_dev

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process each HTTP/WS request to propagate session context."""
        if scope["type"] not in ("http", "websocket"):
            # Pass through lifespan and other ASGI events untouched
            await self.app(scope, receive, send)
            return

        await self._handle(scope, receive, send)

    async def _handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process each HTTP/WS request to propagate session context.

        This ensures both trace correlation and context propagation across
        downstream services or async tasks.
        """
        connection_type = scope["type"]  # "http" or "websocket"

        # Read incoming headers
        raw_headers = {k.decode(): v.decode() for k, v in scope.get("headers", [])}
        headers = ObserveHeaders.model_validate(raw_headers)

        # Get session_id from headers
        try:
            baggage_dict = dict(item.split("=") for item in headers.baggage.split(",")) if headers.baggage else {}
        except ValueError:
            baggage_dict = {}

        session_id = headers.session_id or baggage_dict.get("session.id")  # pyrefly: ignore[bad-assignment]

        # If session_id is missing, generate it only in local environments,
        # where we simulate AWS behavior that normally populates this value
        if session_id is None and self.local_dev:
            session_id: str = str(uuid4())

        _context = ObserveContext(
            actor_id=headers.actor_id, rho_trace_id=headers.rho_trace_id, session_id=session_id
        )
        set_context(context=_context)

        # Attach session ID to OTEL baggage (propagates across services)
        ctx = otel_baggage.set_baggage("session.id", session_id)
        token = context.attach(ctx)

        # Add session ID as span attribute for observability
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute("agentcore.session_id", session_id)

        try:
            if connection_type == "http":
                await self._handle_http(scope, receive, send, _context)
            else:
                # WebSocket: no response object to attach headers to,
                # context is propagated via OTEL baggage only
                await self.app(scope, receive, send)
        finally:
            context.detach(token)

    async def _handle_http(self, scope: Scope, receive: Receive, send: Send, _context: ObserveContext) -> None:
        """Wrap send callable to inject response headers for HTTP."""

        async def send_with_headers(message: Any) -> None:
            # Intercept the HTTP response start message to inject headers
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))

                if _context.actor_id:
                    h_ = f"{HEADER_BEDROCK_ACTOR_ID.lower()}".encode()
                    headers[h_] = _context.actor_id.encode()
                if _context.session_id:
                    h_ = f"{HEADER_BEDROCK_SESSION_ID.lower()}".encode()
                    headers[h_] = _context.session_id.encode()

                message = {**message, "headers": list(headers.items())}

            await send(message)

        await self.app(scope, receive, send_with_headers)
