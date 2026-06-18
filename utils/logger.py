from __future__ import annotations

import logging
import os


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    level = logging.DEBUG if os.getenv("TRUTHLAYER_DEBUG") == "1" else logging.INFO
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
