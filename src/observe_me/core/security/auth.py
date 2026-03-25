"""Security middleware."""

from collections.abc import Callable
from enum import StrEnum
from typing import ClassVar

from starlette import status
from starlette.datastructures import Headers
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from observe_me.core.logger_api import get_logger
from observe_me.core.security.idp.idp_adapter import IDPAdapter
from observe_me.core.security.idp.idp_factory import IDPFactory

logger = get_logger(__name__)


class DType(StrEnum):
    """Data types."""

    KEYCLOAK = "keycloak"
    COGNITO = "cognito"


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware Starlette que valida token Bearer y guarda payload/roles en request.state.

    Compatible con mcp.http_app() al ser ASGI estándar.
    """

    public_paths: ClassVar[list[str]] = ["/health", "/docs", "/openapi.json"]

    def __init__(
        self, app: Callable | None = None, provider: DType = DType.KEYCLOAK, verify_token: bool = False
    ) -> None:
        """Instance of middleware."""
        super().__init__(app)
        self.idp_factory = IDPFactory(provider, verify_token)
        self.idp_adapter: IDPAdapter = self.idp_factory.get_idp()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Dispatcher of authentification."""
        if request.url.path.startswith(tuple(self.public_paths)):
            return await call_next(request)

        logger.debug("Dispatcher authentification.")

        try:
            request = await self.validate(request)
            response = await call_next(request)
            return response
        except HTTPException as e:
            logger.error(f"Exception raised {e.detail}")
            return JSONResponse(status_code=e.status_code, content=e.detail)
        except Exception as exc:
            logger.error(f"Error in middleware {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content="Internal Server Error: Middleware"
            )

    async def validate(self, request: Request) -> Request:
        """Validate function."""
        headers = Headers(scope=request.scope)
        authorization = headers.get("authorization")

        if not authorization or not authorization.startswith("Bearer "):
            logger.error("Missing or invalid authorization header")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

        token = authorization.replace("Bearer ", "", 1).strip()

        try:
            user_payload = self.idp_adapter.get_payload(token)
            roles = self.idp_adapter.get_roles(user_payload)
            logger.debug(f"Token válido → sub: {user_payload.get('sub')}, roles: {roles}")

            request.state.user = user_payload
            request.state.roles = roles
        except Exception as e:
            logger.error("Token validation error")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials"
            ) from e

        return request
