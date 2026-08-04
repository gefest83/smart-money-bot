from pathlib import Path
import sys

from loguru import logger

from app.core.config import settings


def setup_logger() -> None:
    """Настройка логирования."""

    log_dir = Path(settings.LOG_PATH)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Удаляем стандартный логгер
    logger.remove()

    # Вывод в консоль
    logger.add(
        sys.stdout,
        level="INFO",
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level:<8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
    )

    # Запись в файл
    logger.add(
        log_dir / "smart_money.log",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | "
               "{name}:{function}:{line} - {message}",
    )


__all__ = ["logger", "setup_logger"]