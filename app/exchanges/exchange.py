from __future__ import annotations
import ccxt
from typing import Any


class ExchangeBase:
    """Light wrapper interface for exchanges."""

    def connect(self) -> None:
        raise NotImplementedError

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 250) -> list[list[float]]:
        raise NotImplementedError

    def fetch_balance(self) -> dict:
        return {}

    def create_order(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def fetch_order(self, order_id: str) -> Any:
        raise NotImplementedError

    def cancel_order(self, order_id: str) -> Any:
        raise NotImplementedError

    def fetch_ticker(self, symbol: str) -> dict:
        return {}

    def close(self) -> None:
        pass


class CCXTExchange(ExchangeBase):
    # map friendly exchange ids to ccxt ids when necessary
    SUPPORTED = {"binance", "bybit", "okx", "bingx", "mexc"}

    def __init__(
        self,
        id: str = "binance",
        testnet: bool = True,
        api_key: str | None = None,
        secret: str | None = None,
        market: str = "spot",
    ):
        self.id = id
        self.testnet = testnet
        self.api_key = api_key
        self.secret = secret
        self.client: ccxt.Exchange | None = None
        self.market = market  # 'spot' or 'futures'

    def connect(self) -> None:
        ex_id = self.id
        if ex_id not in self.SUPPORTED:
            ex_id = self.id

        try:
            ex_cls = getattr(ccxt, ex_id)
        except Exception as exc:
            self.client = ccxt.Exchange({})
            raise RuntimeError(f"Exchange {self.id} not supported in CCXT: {exc}")

        params: dict[str, Any] = {
            "apiKey": self.api_key or "",
            "secret": self.secret or "",
            "enableRateLimit": True,
        }

        if self.market and self.market.lower() in ("futures", "future"):
            params.setdefault("options", {})
            params["options"]["defaultType"] = "future"

        self.client = ex_cls(params)

        if self.testnet:
            try:
                if hasattr(self.client, "set_sandbox_mode"):
                    self.client.set_sandbox_mode(True)
            except Exception:
                pass

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 250) -> list[list[float]]:
        if self.client is None:
            raise RuntimeError("Exchange not connected")
        return self.client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def fetch_balance(self) -> dict:
        if self.client is None:
            return {}
        try:
            return self.client.fetch_balance()
        except Exception:
            return {}

    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        amount: float,
        price: float | None = None,
        params: dict | None = None,
    ) -> Any:
        if self.client is None:
            raise RuntimeError("Exchange not connected")
        params = params or {}
        try:
            # preferred call with named args where supported
            return self.client.create_order(symbol, order_type, side.lower(), amount, price, params)
        except Exception as exc:
            # some exchanges vary positional args; try common fallback
            try:
                return self.client.create_order(symbol, order_type, side.lower(), amount)
            except Exception:
                raise exc

    def fetch_order(self, order_id: str) -> Any:
        if self.client is None:
            return None
        try:
            return self.client.fetch_order(order_id)
        except Exception:
            return None

    def cancel_order(self, order_id: str) -> Any:
        if self.client is None:
            return None
        try:
            return self.client.cancel_order(order_id)
        except Exception:
            return None

    def fetch_ticker(self, symbol: str) -> dict:
        if self.client is None:
            return {}
        try:
            return self.client.fetch_ticker(symbol)
        except Exception:
            try:
                ohlcv = self.client.fetch_ohlcv(symbol, timeframe='1m', limit=1)
                if ohlcv and len(ohlcv) > 0:
                    last = ohlcv[-1]
                    return {'last': last[4], 'timestamp': last[0]}
            except Exception:
                pass
        return {}

    def close(self) -> None:
        self.client = None
