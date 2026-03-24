"""Security middleware.
"""

from collections.abc import Callable
from logging import getLogger

from starlette.datastructures import Headers
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from observe_me.core.security.idp.idp_adapter import IDPAdapter
from observe_me.core.security.idp.idp_factory import IDPFactory

logger = getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware Starlette que valida token Bearer y guarda payload/roles
    en request.state para que las rutas/tools lo puedan usar.

    Compatible con mcp.http_app() al ser ASGI estándar.
    """

    def __init__(
        self, app: Callable, provider: str = "logto", verify_token: bool = False
    ) -> None:
        """Instance of middleware."""
        super().__init__(app)
        self.idp_factory = IDPFactory(provider, verify_token)
        self.idp_adapter: IDPAdapter = self.idp_factory.get_idp()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Dispatcher of authentification."""
        logger.debug("Dispatcher authentification.")
        headers = Headers(scope=request.scope)
        authorization = headers.get("authorization")

        user_payload = {}
        roles: set[str] = set()

        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "", 1).strip()

            try:
                user_payload = self.idp_adapter.get_payload(token)
                roles = self.idp_adapter.get_roles(user_payload)
                logger.debug(f"Token válido → sub: {user_payload.get('sub')}, roles: {roles}")

            except Exception as exc:
                logger.error(f"Error al validar token: {exc}", exc_info=True)

                return JSONResponse(status_code=401, content={"detail": "Invalid authentication credentials"})

        request.state.user = user_payload
        request.state.roles = roles

        try:
            response = await call_next(request)
            return response

        except Exception as exc:
            logger.exception("Error inesperado después del middleware", exc_info=exc)
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
