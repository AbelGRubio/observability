"""HTTP header parsing utilities for agent execution.

Defines typed models and helpers to extract request headers and convert
them into structured data consumed by the agent runtime.
"""

from typing import Annotated

from fastapi import Header
from pydantic import BaseModel, ConfigDict, Field

HEADER_BEDROCK_ACTOR_ID = "X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actor-Id"
HEADER_BEDROCK_RHO_TRACE_ID = "X-Amzn-Bedrock-AgentCore-Runtime-Custom-Rho-Trace-Id"
HEADER_BEDROCK_SESSION_ID = "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id"
HEADER_BEDROCK_STREAMING = "X-Amzn-Bedrock-AgentCore-Runtime-Custom-Streaming"


class ObserveHeaders(BaseModel):
    """Parsed request headers used during agent invocation.

    Encapsulates optional session and streaming control information.
    """

    model_config = ConfigDict(populate_by_name=True)

    actor_id: str | None = Field(
        alias=HEADER_BEDROCK_ACTOR_ID,
        validation_alias=HEADER_BEDROCK_ACTOR_ID.lower(),
        default=None,
        description="Unique identifier for the actor using the agent.",
    )
    baggage: str | None = Field(default=None, description="Propagates custom key-value across service boundaries.")
    rho_trace_id: str | None = Field(
        alias=HEADER_BEDROCK_RHO_TRACE_ID,
        validation_alias=HEADER_BEDROCK_RHO_TRACE_ID.lower(),
        default=None,
        description=(
            "Identifier for the RHO corporate observability system. "
            "This corporate end-to-end identifier is used to correlate the "
            "request across all internal bank systems."
        ),
    )
    session_id: str | None = Field(
        alias=HEADER_BEDROCK_SESSION_ID,
        validation_alias=HEADER_BEDROCK_SESSION_ID.lower(),
        default=None,
        description=(
            "Unique identifier for the agent session. In local environments, "
            "provide a custom string to test agent memory persistence. In "
            "production, AWS Bedrock automatically populates this header."
        ),
    )
    streaming: bool = Field(
        alias=HEADER_BEDROCK_STREAMING,
        validation_alias=HEADER_BEDROCK_STREAMING.lower(),
        default=False,
        description="Toggle to enable or disable streaming responses from the agent.",
    )


HeadersDep = Annotated[ObserveHeaders, Header()]
