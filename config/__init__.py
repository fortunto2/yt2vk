from .config import *
try:
    from .config_local import *
except ImportError:
    pass

import logging.config


logging.config.dictConfig(LOGGING_CONFIG)

