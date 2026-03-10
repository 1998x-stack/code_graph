"""
Logger setup using loguru.
"""

import sys
from loguru import logger
from ..config.settings import settings


def setup_logger():
    """Setup the global logger with the configured settings."""
    logger.remove()
    
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
        colorize=True
    )
    
    return logger


def get_logger(name: str = __name__):
    """Get a logger instance with the given name."""
    return logger


# Setup the global logger when this module is imported
setup_logger()