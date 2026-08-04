from __future__ import annotations
from loguru import logger
from pathlib import Path
from .config import settings

def setup_logger() -> None:
    log_dir = settings.LOG_PATH
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "smart_money.log"

    logger.remove()
    logger.add(lambda msg: print(msg, end=""), colorize=True)
    logger.add(str(log_file), rotation="10 MB", retention="10 days")

# expose logger

