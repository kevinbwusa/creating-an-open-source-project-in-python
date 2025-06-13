import logging
import logging.config
import os

LOG_CONFIG = os.getenv("LOG_CONFIG", "logging.conf")

logging.config.fileConfig(LOG_CONFIG, disable_existing_loggers=False)
logger = logging.getLogger("reminder")
