"""Entry point."""

import uvicorn
from observe_core.logger import get_logger, propague_loggers

from observe_api import configure_app, define_app, get_app_settings

logger = get_logger(__name__)

configure_app()
app = define_app()

propague_loggers()


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
