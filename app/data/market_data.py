from __future__ import annotations
from app.exchanges.manager import ExchangeManager


class MarketData:
    def __init__(self, exchange_manager: ExchangeManager):
        self._ex = exchange_manager

    def fetch_candles(self, symbol: str, timeframe: str, limit: int = 250):
        return self._ex.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
