"""
RAVAND OS – Logging Configuration
Professional structured logging with rotating file handlers.
Produces both human-readable console output and machine-parsable file logs.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path

from app.core.config import get_settings

_configured: bool = False


def _build_console_handler(level: int) -> logging.StreamHandler:
    """Create a colour-friendly console handler."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    return handler


def _build_rotating_handler(
    log_dir: Path,
    filename: str,
    level: int,
    max_bytes: int,
    backup_count: int,
) -> logging.handlers.RotatingFileHandler:
    """Create a rotating file handler."""
    log_dir.mkdir(parents=True, exist_ok=True)
    filepath = log_dir / filename
    handler = logging.handlers.RotatingFileHandler(
        filepath,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setLevel(level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    return handler


def configure_logging() -> None:
    """
    Configure the root logger and module-level loggers for RAVAND OS.
    Safe to call multiple times – only executes once.
    """
    global _configured
    if _configured:
        return
    _configured = True

    settings = get_settings()
    log_dir = Path(settings.LOG_DIR)
    numeric_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # let handlers filter by level

    # Console – INFO+ by default, DEBUG in debug mode
    console_level = logging.DEBUG if settings.DEBUG else numeric_level
    root_logger.addHandler(_build_console_handler(console_level))

    # General application log – all levels >= configured level
    root_logger.addHandler(
        _build_rotating_handler(
            log_dir=log_dir,
            filename="ravand_os.log",
            level=numeric_level,
            max_bytes=settings.LOG_MAX_BYTES,
            backup_count=settings.LOG_BACKUP_COUNT,
        )
    )

    # Dedicated error log – WARNING and above only
    root_logger.addHandler(
        _build_rotating_handler(
            log_dir=log_dir,
            filename="ravand_os_errors.log",
            level=logging.WARNING,
            max_bytes=settings.LOG_MAX_BYTES,
            backup_count=settings.LOG_BACKUP_COUNT,
        )
    )

    # Silence noisy third-party libraries at WARNING level
    for noisy_lib in ("uvicorn.access", "httpx", "sqlalchemy.engine"):
        logging.getLogger(noisy_lib).setLevel(logging.WARNING)

    logging.getLogger("ravand_os").info(
        "Logging initialised | level=%s | log_dir=%s",
        settings.LOG_LEVEL,
        log_dir.resolve(),
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger under the 'ravand_os' namespace.
    Usage:
        logger = get_logger(__name__)
    """
    configure_logging()
    return logging.getLogger(f"ravand_os.{name}")
