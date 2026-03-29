"""Entry point."""

import logging

import uvicorn

from observe_me import configure_app, define_app, get_app_settings
from observe_me.core.logger_api import get_logger

logger = get_logger(__name__)

configure_app()
app = define_app()

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
        host=get_app_settings().api_ip,
        port=get_app_settings().api_port,
        log_config=None,
        reload=False,
    )
    logger.debug("Ending.")
