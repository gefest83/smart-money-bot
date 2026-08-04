import time

import ccxt
from loguru import logger

from app.config.env import env


class ExchangeManager:
    """
    Управление подключением к биржам через CCXT.
    """

    def __init__(self):

        self.exchange = None

    def connect(self):

        exchange_name = env.exchange.lower()

        config = {
            "enableRateLimit": True,
        }

        if env.has_keys():

            config.update(
                {
                    "apiKey": env.api_key,
                    "secret": env.api_secret,
                }
            )

        else:

            logger.warning(
                """
API ключи не найдены.

Работаем только в режиме чтения.
Баланс и реальные ордера недоступны.
"""
            )

        if exchange_name == "binance":

            self.exchange = ccxt.binance(config)

        else:

            raise Exception(
                f"Unsupported exchange: {exchange_name}"
            )

        if env.testnet:

            logger.warning("TESTNET MODE ENABLED")

            self.exchange.set_sandbox_mode(True)

        logger.success(
            f"Подключение к {env.exchange.upper()} успешно"
        )

    def load_markets(self):

        return self.exchange.load_markets()

    def fetch_ohlcv(
        self,
        symbol,
        timeframe,
        limit=300,
        since=None,
    ):

        MAX_LIMIT = 1000

        if limit <= MAX_LIMIT:

            return self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                since=since,
                limit=limit,
            )

        logger.info(
            f"Loading {limit} candles..."
        )

        candles = []

        current_since = since

        while len(candles) < limit:

            batch_limit = min(
                MAX_LIMIT,
                limit - len(candles),
            )

            batch = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                since=current_since,
                limit=batch_limit,
            )

            if not batch:
                break

            candles.extend(batch)

            logger.info(
                f"Loaded {len(candles)}/{limit}"
            )

            current_since = batch[-1][0] + 1

            time.sleep(
                self.exchange.rateLimit / 1000
            )

            if len(batch) < batch_limit:
                break

        unique = []

        seen = set()

        for candle in candles:

            ts = candle[0]

            if ts not in seen:

                seen.add(ts)

                unique.append(candle)

        return unique[:limit]

    def fetch_ticker(
        self,
        symbol="BTC/USDT",
    ):

        return self.exchange.fetch_ticker(symbol)

    def fetch_balance(self):

        if not env.has_keys():

            raise Exception(
                "API keys missing"
            )

        return self.exchange.fetch_balance()

    def create_order(
        self,
        symbol,
        type,
        side,
        amount,
    ):

        if not env.live_enabled:

            raise Exception(
                "LIVE ORDERS DISABLED"
            )

        return self.exchange.create_order(
            symbol,
            type,
            side,
            amount,
        )

    def close(self):

        logger.info(
            "Exchange connection closed"
        )