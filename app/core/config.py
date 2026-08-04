from __future__ import annotations
from pathlib import Path
from pydantic import BaseSettings

class Settings(BaseSettings):
    SYMBOL: str = "BTC/USDT"
    TIMEFRAME: str = "15m"
    EXCHANGE: str = "binance"
    MARKET: str = "spot"  # spot or futures
    MODE: str = "paper"  # paper, backtest, live
    TESTNET: bool = True
    DATA_PATH: Path = Path("data")
    LOG_PATH: Path = Path("logs")
    TELEGRAM_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None
    RISK_PERCENT: float = 1.0

    class Config:
        env_file = ".env"

settings = Settings()
