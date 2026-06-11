"""Entry point."""

import logging

import uvicorn
from observe_core.logger_api import get_logger
from observe_mcp.configure_app import get_asgi_app, load_tools

logger = get_logger(__name__)

load_tools()

app = get_asgi_app()

# To put all loggers in same format.
for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    uvicorn_logger = logging.getLogger(name)
    uvicorn_logger.handlers = logger.handlers
    uvicorn_logger.setLevel(logging.DEBUG)
    uvicorn_logger.propagate = False


if __name__ == "__main__":
    logger.debug("Starting...")
    uvicorn.run(
        app=app,
        host="127.0.0.1",
        port=8000,
        log_config=None,
        reload=False,
    )
    logger.debug("Ending.")
