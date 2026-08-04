from __future__ import annotations
import threading
from app.runner.engine import TradingEngine
from app.core.logger import logger

_engine_thread = None
_engine_instance = None


def start_engine(mode: str = 'paper', interval: int = 10, amount: float = 1.0) -> None:
    global _engine_thread, _engine_instance
    if _engine_instance and _engine_thread and _engine_thread.is_alive():
        logger.info('Engine already running')
        return
    _engine_instance = TradingEngine(
        mode=mode,
        poll_interval=interval,
        order_amount=amount,
        handle_signals=False,
    )
    _engine_thread = threading.Thread(
        target=_engine_instance.start,
        daemon=True,
    )
    _engine_thread.start()


def stop_engine() -> None:
    if _engine_instance:
        _engine_instance.stop()
    if _engine_thread:
        _engine_thread.join(timeout=10)


def engine_status() -> dict:
    return {
        'running': bool(_engine_thread and _engine_thread.is_alive()),
        'mode': _engine_instance.mode if _engine_instance else None,
        'poll_interval': _engine_instance.poll_interval if _engine_instance else None,
    }
