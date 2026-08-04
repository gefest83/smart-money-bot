from __future__ import annotations
from prometheus_client import Counter, Gauge

trades_closed_total = Counter(
    "smb_trades_closed_total",
    "Total number of closed trades",
)
signals_generated_total = Counter(
    "smb_signals_generated_total",
    "Total number of generated signals",
)
engine_running = Gauge(
    "smb_engine_running",
    "Trading engine running (1) or stopped (0)",
)
