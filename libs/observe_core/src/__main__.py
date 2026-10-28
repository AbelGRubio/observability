
import observe_core
from logging import getLogger
logger = getLogger(__name__)


if __name__ == '__main__':
    logger.detail("Detail level")
    logger.debug(f'dimportado {observe_core.__name__}')
    logger.info(f'dimportado info {observe_core.__name__}')
    logger.warning(f'dimportado warning {observe_core.__name__}')
    f = 1