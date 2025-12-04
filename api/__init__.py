import logging
from api.config import config

logger = logging.getLogger("uvicorn")
logger.setLevel(config.api_log_level)