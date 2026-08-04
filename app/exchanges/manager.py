from __future__ import annotations
from .exchange import CCXTExchange
from app.core.config import settings

class ExchangeManager:
    def __init__(self):
        self.exchange = CCXTExchange(id=settings.EXCHANGE, testnet=settings.TESTNET)

    def connect(self) -> None:
        self.exchange.connect()

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 250):
        return self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def close(self) -> None:
        self.exchange.close()
