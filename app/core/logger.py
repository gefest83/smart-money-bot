from __future__ import annotations
from loguru import logger
from .config import settings
from app.webapp.log_buffer import push_log


def _buffer_sink(message) -> None:
    record = message.record
    text = message
    try:
        # message already formatted
        push_log(str(message).rstrip('\n'))
    except Exception:
        pass


def setup_logger() -> None:
    log_dir = settings.LOG_PATH
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "smart_money.log"

    logger.remove()
    # stdout
    logger.add(lambda msg: print(msg, end=""), colorize=True)
    # file
    logger.add(str(log_file), rotation="10 MB", retention="10 days")
    # in-memory buffer for web UI
    logger.add(_buffer_sink, level="INFO")

# expose logger
