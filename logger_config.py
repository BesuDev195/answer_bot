"""
logger_config.py

FR-07: Logging — user questions, matched FAQ, unanswered questions, timestamp.

Writes logs to both the console (useful when running via Docker/systemd,
where logs are captured by the platform) and a rotating log file on disk.
"""

import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger() -> logging.Logger:
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger("faq_bot")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotate at 5MB, keep 5 backups so the log never grows unbounded.
    file_handler = RotatingFileHandler(
        "logs/bot.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
