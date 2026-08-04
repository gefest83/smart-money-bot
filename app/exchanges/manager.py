from __future__ import annotations
from .exchange import CCXTExchange
from app.core.config import settings


class ExchangeManager:
    def __init__(self, api_key: str | None = None, secret: str | None = None):
        self.exchange = CCXTExchange(
            id=settings.EXCHANGE,
            testnet=settings.TESTNET,
            api_key=api_key,
            secret=secret,
            market=settings.MARKET,
        )

    def connect(self) -> None:
        self.exchange.connect()

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 250):
        return self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def fetch_balance(self) -> dict:
        return self.exchange.fetch_balance()

    def create_order(self, *args, **kwargs):
        return self.exchange.create_order(*args, **kwargs)

    def fetch_order(self, order_id: str):
        if hasattr(self.exchange, 'fetch_order'):
            try:
                return self.exchange.client.fetch_order(order_id)
            except Exception:
                return None
        return None

    def cancel_order(self, order_id: str):
        if hasattr(self.exchange, 'cancel_order'):
            try:
                return self.exchange.client.cancel_order(order_id)
            except Exception:
                return None
        return None

    def close(self) -> None:
        self.exchange.close()
