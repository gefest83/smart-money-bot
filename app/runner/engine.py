from __future__ import annotations
import threading
import signal
import time
import traceback
from typing import Optional
from app.core.logger import logger, setup_logger
from app.exchanges.manager import ExchangeManager
from app.strategies.smart_money import SmartMoneyStrategy
from app.trader.executor import Executor
from app.database.trades import TradeDatabase
from app.backtest.report import BacktestReport
from app.core.config import settings


class TradingEngine:
    def __init__(self, mode: str = 'paper', poll_interval: int = 10, order_amount: float = 1.0):
        self.mode = mode
        self.poll_interval = poll_interval
        self.order_amount = order_amount
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self.exchange_manager = ExchangeManager()
        self.strategy = SmartMoneyStrategy()
        self.executor = Executor()
        self.db = TradeDatabase(path=settings.DATA_PATH / "trades.db")
        self.reporter = BacktestReport()
        self.notifier = None  # optional TelegramNotifier if configured

    def start(self):
        setup_logger()
        logger.info(f"Starting trading engine in {self.mode} mode. Poll every {self.poll_interval}s")

        # handle signals for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            self.exchange_manager.connect()
        except Exception as exc:
            logger.exception("Failed to connect to exchange manager")

        # main loop
        try:
            while not self._stop_event.is_set():
                try:
                    self._tick()
                except Exception as exc:
                    logger.error(f"Error during tick: {exc}")
                    logger.debug(traceback.format_exc())
                # wait with small sleeps to be responsive to shutdown
                for _ in range(int(max(1, self.poll_interval))):
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)
        finally:
            logger.info("Shutting down trading engine")
            try:
                self.exchange_manager.close()
            except Exception:
                pass
            logger.info("Engine stopped")

    def stop(self):
        logger.info("Stop requested")
        self._stop_event.set()

    def _signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully")
        self.stop()

    def _tick(self):
        # fetch market data
        try:
            candles = self.exchange_manager.fetch_ohlcv(settings.SYMBOL, settings.TIMEFRAME, limit=200)
        except Exception as exc:
            logger.warning(f"Failed to fetch candles: {exc}")
            return

        # latest price
        try:
            ticker = self.exchange_manager.exchange.fetch_ticker(settings.SYMBOL)
            price = float(ticker.get('last') or candles[-1][4])
        except Exception:
            price = float(candles[-1][4])

        # monitor open position first
        if self.executor.in_position:
            closed = None
            try:
                closed = self.executor.update_price(price)
            except Exception as exc:
                logger.warning(f"Error updating price in executor: {exc}")

            if closed:
                for t in closed:
                    logger.info(f"Closed trade: {t}")
                    try:
                        self.db.add_trade(t)
                    except Exception:
                        logger.exception("Failed to save trade to DB")
                # report on each closure
                try:
                    self.reporter.save(closed)
                except Exception:
                    logger.exception("Failed to save report")
            return

        # if no position: generate signals and open if any
        signals = self.strategy.generate_signals(candles)
        if not signals:
            logger.debug("No signals")
            return

        # pick most recent signal (highest index)
        latest_idx = max(signals.keys())
        sig = signals[latest_idx]
        # Only trigger on most recent bar
        if latest_idx < len(candles) - 1:
            logger.debug("Latest signal is not on last candle; skipping until confirmed")
            return

        logger.info(f"Found new signal: {sig.side} at {sig.entry} reason={sig.reason}")

        if self.mode == 'paper' or settings.MODE == 'paper':
            # open via executor
            opened = self.executor.process_signal(sig, amount=self.order_amount)
            if opened:
                logger.info("Opened PAPER position")
            else:
                logger.info("Failed to open PAPER position (already in position?)")
        else:
            # live: create market order and emulate fill
            try:
                order = None
                try:
                    order = self.exchange_manager.exchange.create_order(sig.symbol, sig.side, 'market', self.order_amount, None, {})
                except TypeError:
                    # try ccxt positional
                    order = self.exchange_manager.exchange.create_order(sig.symbol, 'market', sig.side.lower(), self.order_amount)
                except Exception as exc:
                    logger.exception(f"Live order failed: {exc}")

                if order:
                    # derive fill price
                    price_fill = None
                    if isinstance(order, dict):
                        price_fill = order.get('average') or order.get('price')
                    try:
                        if price_fill is None:
                            # fallback to ticker
                            t = self.exchange_manager.exchange.fetch_ticker(sig.symbol)
                            price_fill = float(t.get('last'))
                    except Exception:
                        price_fill = sig.entry

                    # construct in-memory position
                    fake_signal = sig
                    fake_signal.entry = float(price_fill)
                    opened = self.executor.process_signal(fake_signal, amount=self.order_amount)
                    if opened:
                        logger.info(f"Opened LIVE position (simulated fill at {price_fill})")
                    else:
                        logger.info("Executor rejected opening after live order")

            except Exception as exc:
                logger.exception(f"Exception during live open: {exc}")


def run_engine_forever(mode: str = 'paper', interval: int = 10):
    engine = TradingEngine(mode=mode, poll_interval=interval)
    engine.start()


if __name__ == "__main__":
    run_engine_forever()
