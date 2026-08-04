import ccxt.async_support as ccxt

from app.core.config import settings
from app.core.logger import logger


class BinanceExchange:

    def __init__(self):

        self.exchange = ccxt.binance({
            "apiKey": settings.API_KEY,
            "secret": settings.API_SECRET,
            "enableRateLimit": True,
        })

        if settings.TESTNET:
            self.exchange.set_sandbox_mode(True)

    async def connect(self):

        await self.exchange.load_markets()

        logger.success("Connected to Binance")

        return self.exchange

    async def markets(self):

        return self.exchange.markets

    async def balance(self):

        return await self.exchange.fetch_balance()

    async def candles(self):

        return await self.exchange.fetch_ohlcv(
            settings.SYMBOL,
            settings.TIMEFRAME,
            limit=200,
        )

    async def close(self):

        await self.exchange.close()