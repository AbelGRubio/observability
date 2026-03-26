# =========================
# Builder
# =========================
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ARG UV_INDEX_USERNAME
ARG UV_INDEX_PASSWORD

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_DEV=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local \
    HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Copiar solo archivos para deps
COPY pyproject.toml README.md ./

COPY src/ src/
COPY ./cfg ./cfg

# Instalar dependencias + proyecto, directo en el Python del sistema
RUN uv sync --no-dev

# Comando por defecto
CMD sh -c "opentelemetry-instrument uvicorn src.__main__:app --host ${HOST} --port ${PORT}"
