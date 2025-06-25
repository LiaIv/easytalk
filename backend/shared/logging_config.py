"""Structlog JSON logging configuration for FastAPI services."""
from __future__ import annotations

import logging
import sys
import structlog


def configure_logging(level: int = logging.INFO) -> None:
    """Configure structlog to output JSON lines to stdout."""
    # Configure *standard* logging to go through structlog
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
