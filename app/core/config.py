from __future__ import annotations
from pathlib import Path
try:
    from pydantic import BaseSettings  # type: ignore
except Exception:
    # pydantic v2 moved BaseSettings to pydantic-settings package
    from pydantic_settings import BaseSettings  # type: ignore


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
    LEVERAGE: int = 1
    PAPER_BALANCE: float = 1000.0

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
