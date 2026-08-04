from __future__ import annotations
import sys
import argparse
from pathlib import Path
from app.core.logger import setup_logger, logger
from app.core.config import settings
from app.exchanges.manager import ExchangeManager
from app.data.market_data import MarketData
from app.strategies.smart_money import SmartMoneyStrategy
from app.trader.executor import Executor
from app.database.trades import TradeDatabase
from app.backtest.report import BacktestReport


def run_backtest():
    setup_logger()
    logger.info("Backtest mode")
    ex = ExchangeManager()
    ex.connect()
    md = MarketData(ex)
    candles = md.fetch_candles(settings.SYMBOL, settings.TIMEFRAME, limit=1000)
    strat = SmartMoneyStrategy()
    signals = strat.generate_signals(candles)
    exec = Executor()
    db = TradeDatabase(path=settings.DATA_PATH / "trades.db")
    closed = []
    for i, c in enumerate(candles):
        price = float(c[4])
        sig = signals.get(i)
        if sig and not exec.in_position:
            exec.process_signal(sig, amount=1.0)
        ct = exec.update_price(price)
        if ct:
            for t in ct:
                db.add_trade(t)
                closed.append(t)
    if exec.in_position:
        lp = float(candles[-1][4])
        t = exec.close_position(lp, reason="End of backtest")
        if t:
            db.add_trade(t)
            closed.append(t)
    ex.close()
    if closed:
        report = BacktestReport()
        path = report.save(closed)
        logger.success(f"Backtest finished. Report saved: {path}")
    else:
        logger.warning("No trades closed during backtest")


def run_paper():
    setup_logger()
    logger.info("Paper mode (single-run) starting")
    # Run same flow as backtest but with smaller limits to simulate live behaviour
    ex = ExchangeManager()
    ex.connect()
    md = MarketData(ex)
    candles = md.fetch_candles(settings.SYMBOL, settings.TIMEFRAME, limit=500)
    strat = SmartMoneyStrategy()
    signals = strat.generate_signals(candles)
    exec = Executor()
    db = TradeDatabase(path=settings.DATA_PATH / "trades.db")
    for i, c in enumerate(candles):
        price = float(c[4])
        sig = signals.get(i)
        if sig and not exec.in_position:
            exec.process_signal(sig, amount=1.0)
        ct = exec.update_price(price)
        if ct:
            for t in ct:
                db.add_trade(t)
    if exec.in_position:
        lp = float(candles[-1][4])
        t = exec.close_position(lp, reason="End of paper run")
        if t:
            db.add_trade(t)
    ex.close()
    logger.info("Paper run finished")


def run_live():
    setup_logger()
    logger.info("Live mode (testnet recommended)")
    # Live mode requires API keys and careful handling; here we only connect and log the balance
    ex = ExchangeManager()
    ex.connect()
    bal = ex.fetch_balance()
    logger.info(f"Balance snapshot: {bal}")
    ex.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["backtest", "paper", "live", "web"], default=settings.MODE)
    args = parser.parse_args()
    mode = args.mode

    if mode == "backtest":
        run_backtest()
    elif mode == "paper":
        run_paper()
    elif mode == "live":
        run_live()
    elif mode == "web":
        # run FastAPI web UI
        try:
            import uvicorn
            logger.info("Starting web UI on http://127.0.0.1:8000")
            uvicorn.run("app.webapp.api:app", host="0.0.0.0", port=8000, log_level="info")
        except Exception as exc:
            logger.exception("Failed to start web server")
    else:
        print("Unknown mode")
