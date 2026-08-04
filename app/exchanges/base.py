from abc import ABC, abstractmethod


class BaseExchange(ABC):
    """
    Базовый интерфейс обменника.
    """

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def load_markets(self):
        pass

    @abstractmethod
    async def fetch_balance(self):
        pass

    @abstractmethod
    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500):
        pass