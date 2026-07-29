"""
XOS Logger — lightweight structured logger for the platform.
"""

from __future__ import annotations

import logging
import sys

_log_format = logging.Formatter("[%(levelname).1s] %(asctime)s %(name)s — %(message)s")


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.INFO)
        h.setFormatter(_log_format)
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger
