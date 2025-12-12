"""
Centralized logging configuration for OmniCore services.
"""

import logging
import sys
from typing import Optional
from datetime import datetime


class OmniCoreFormatter(logging.Formatter):
    """Custom formatter for OmniCore logs."""

    def __init__(self, service_name: str = "omnicore"):
        self.service_name = service_name
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.utcnow().isoformat()
        level = record.levelname
        message = record.getMessage()

        # Include exception info if present
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            message = f"{message}\n{exc_text}"

        return f"[{timestamp}] [{self.service_name}] [{level}] {record.name}: {message}"


def setup_logging(
    service_name: str = "omnicore",
    level: str = "INFO",
) -> None:
    """
    Set up logging configuration for a service.

    Args:
        service_name: Name of the service for log identification
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Get the numeric log level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # Set formatter
    formatter = OmniCoreFormatter(service_name)
    console_handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
