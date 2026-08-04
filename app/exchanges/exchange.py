from __future__ import annotations
import ccxt
from typing import Any

class ExchangeBase:
    """Light wrapper interface for exchanges."""

    def connect(self) -> None:
        raise NotImplementedError

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 250) -> list[list[float]]:
        raise NotImplementedError

    def close(self) -> None:
        pass

class CCXTExchange(ExchangeBase):
    def __init__(self, id: str = "binance", testnet: bool = True, api_key: str | None = None, secret: str | None = None):
        self.id = id
        self.testnet = testnet
        self.api_key = api_key
        self.secret = secret
        self.client: ccxt.Exchange | None = None

    def connect(self) -> None:
        ex_cls = getattr(ccxt, self.id)
        params: dict[str, Any] = {}
        if self.id == "binance":
            params = {"enableRateLimit": True}
            if self.testnet:
                params["options"] = {"defaultType": "future"}

        self.client = ex_cls({"apiKey": self.api_key or "", "secret": self.secret or "", **params})
        # testnet config if supported
        if self.testnet and hasattr(self.client, "set_sandbox_mode"):
            try:
                self.client.set_sandbox_mode(True)
            except Exception:
                pass

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 250) -> list[list[float]]:
        if self.client is None:
            raise RuntimeError("Exchange not connected")
        return self.client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def close(self) -> None:
        # ccxt clients don't usually need explicit close
        self.client = None
