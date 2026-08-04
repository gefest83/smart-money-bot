from __future__ import annotations
import sys

from app.backtest.report import BacktestReport
from app.config.env import env
from app.core.config import settings
from app.core.logger import logger, setup_logger
from app.database.statistics import TradeStatistics
from app.database.trades import TradeDatabase
from app.exchanges.manager import ExchangeManager
from app.executor.manager import ExecutorManager
from app.strategies.simple import SimpleStrategy


def run() -> int:
    setup_logger()

    logger.info("Запуск Smart Money Bot")
    logger.info(
        f"Exchange={env.exchange}, Symbol={settings.SYMBOL}, Timeframe={settings.TIMEFRAME}"
    )

    exchange = ExchangeManager()
    exchange.connect()

    try:
        candles = exchange.fetch_ohlcv(
            symbol=settings.SYMBOL,
            timeframe=settings.TIMEFRAME,
            limit=250,
        )
    except Exception as exc:
        logger.error(f"Не удалось загрузить свечи: {exc}")
        return 1

    if not candles:
        logger.error("Свечи не возвращены. Проверьте подключение к бирже.")
        return 1

    strategy = SimpleStrategy()
    signals = strategy.generate_signals(candles)

    logger.info("Сигналы рассчитаны")
    logger.info(f"Найдено сигналов: {len(signals)}")

    database = TradeDatabase(path=settings.DATA_PATH / "trades.db")
    executor = ExecutorManager()
    closed_trades = []

    for index, candle in enumerate(candles):
        price = float(candle[4])
        signal = signals.get(index)

        if signal and not executor.in_position:
            result = executor.process_signal(signal)

            if result:
                logger.info(
                    f"Открыта позиция {signal.side} {signal.symbol} по {signal.entry:.2f}"
                )
            else:
                logger.info("Сигнал проигнорирован, позиция уже открыта или не удалось открыть.")

        closed_trade = executor.update_price(price)

        if closed_trade is not None:
            database.add_trade(closed_trade)
            closed_trades.append(closed_trade)

    if executor.in_position:
        last_price = float(candles[-1][4])
        closed_trade = executor.close_position(
            last_price,
            reason="Закрытие по последней свече",
        )

        if closed_trade is not None:
            database.add_trade(closed_trade)
            closed_trades.append(closed_trade)

    if closed_trades:
        report = BacktestReport().save(closed_trades)
        logger.success(f"Отчет сохранен: {report}")
    else:
        logger.warning("Не было закрытых сделок для отчета.")

    TradeStatistics(database).calculate()
    exchange.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
