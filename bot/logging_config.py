"""Logging configuration for the trading bot.

Provides a single setup function that configures rotating file and stream
handlers so every module in the project shares a consistent log format.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
MAX_BYTES = 1_048_576  # 1 MB
BACKUP_COUNT = 3


def setup_logging(log_file: str = "trading_bot.log") -> None:
    """Configure root logger with a rotating file handler and a stream handler.

    Args:
        log_file: Path to the log file. Defaults to 'trading_bot.log'.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(LOG_FORMAT)

    # Rotating file handler captures all levels for post-mortem debugging.
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Stream handler surfaces INFO and above to the console.
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
