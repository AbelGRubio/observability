# telemetry.py
import logging
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.trace import StatusCode
from starlette.middleware.base import BaseHTTPMiddleware


def request_hook(span, scope):
    response = scope.get("response")
    if span and response:
        span.set_attribute("http.status_code", response.status_code)
        if response.status_code >= 400:
            span.set_status(StatusCode.ERROR)


class OTELStatusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        body = await request.body()
        span = trace.get_current_span()
        if span:
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.path", request.url.path)
            span.set_attribute("http.query", str(request.query_params))
            span.set_attribute("http.body", body.decode() if body else "")
        response = await call_next(request)
        if span:
            span.set_attribute("http.status_code", response.status_code)
            # Marcar error si status >= 400
            if response.status_code >= 400:
                span.set_status(StatusCode.ERROR)
            # Registrar output (opcional)
            span.set_attribute("http.response_body", response.body.decode() if hasattr(response, "body") else "")
        return response


def setup_telemetry(app):
    resource = Resource.create({
        "service.name": "fastapi-sqlalchemy-demo"
    })

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
        insecure=True,
    )

    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    # Instrumentación automática
    FastAPIInstrumentor.instrument_app(
        app,
        server_request_hook=request_hook,
    )

    LoggingInstrumentor().instrument(set_logging_format=True)
    logging.basicConfig(level=logging.INFO)
    app.add_middleware(OTELStatusMiddleware)
