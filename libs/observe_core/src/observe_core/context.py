"""Session context for FastAPI with OpenTelemetry context propagation."""

from contextvars import ContextVar

from pydantic import BaseModel, ConfigDict, Field


class ObserveContext(BaseModel):
    """Execution context for the Observe session.

    This model encapsulates the necessary identifiers and metadata required
    to maintain session state and user identity throughout the session's
    lifecycle. It serves as a unified container to pass environment-specific
    contextual information across different layers of the application.

    Attributes:
        actor_id (str | None): The unique identifier for the agent.
        session_id (str | None): The unique identifier for the conversational session.
    """

    model_config = ConfigDict(frozen=True)

    actor_id: str | None = Field(
        default=None, description="The unique identifier for the actor. Required for memory persistence."
    )
    rho_trace_id: str | None = Field(
        default=None, description="The unique identifier for rho. Required for system observability."
    )
    session_id: str | None = Field(
        default=None, description="The unique identifier for the session. Required for memory persistence."
    )


_context_var: ContextVar[ObserveContext | None] = ContextVar("observe_context", default=None)


def get_context() -> ObserveContext | None:
    """Retrieves the current execution context.

    Returns:
        ObserveContext: The current execution context specific to the ongoing request.
    """
    return _context_var.get()


def set_context(context: ObserveContext) -> None:
    """Sets the execution context for the current asynchronous task.

    This function is intended to be used by the API layer (e.g., FastAPI middleware
    or dependencies) to inject the context parsed from incoming request headers.
    It utilizes `contextvars` to ensure that the context is strictly isolated and
    thread-safe per HTTP request, preventing data leaks between concurrent sessions.

    Args:
        context (ObserveContext): The frozen execution context model containing session and actor identifiers.
    """
    if _context_var.get() is not None:
        raise RuntimeError("ObserveContext has already been set for this execution scope and cannot be modified.")

    _context_var.set(context)
