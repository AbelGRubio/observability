"""Api routes definition."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from opentelemetry import trace

from observe_me.config import __version__

v1_router = APIRouter()


@v1_router.get("/route")
def route(name: str) -> JSONResponse:
    """Check if everything is working."""
    status_code = 200
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("mi-operacion") as span:
        span.add_event("Inicio del proceso")

        # tu lógica
        user_id = 123

        span.add_event(
            "Usuario procesado",
            {
                "user.id": f'{name}:{user_id}',
                "resultado": "ok"
            }
        )
    return JSONResponse(content={f"{name}, la version es": __version__}, status_code=status_code)
