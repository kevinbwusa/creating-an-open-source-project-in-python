"""Contains all project configurations"""

import logging
import logging.config
from os import getenv
from re import match

LOG_CONFIG = getenv("LOG_CONFIG", "logging.conf")
logging.config.fileConfig(LOG_CONFIG, disable_existing_loggers=False)

logger = logging.getLogger(__name__)

CORS_ALLOW_ORIGIN = getenv("CORS_ALLOW_ORIGIN")

logger.info("Configuration Parameters:")
for item in dir():
    if not item.startswith("__") and match("^[A-Z-0-9_]+$", item):
        logger.info("%s: %s", item, vars()[item])
