from __future__ import annotations
from typing import Dict, List
from statistics import mean

from app.models import Signal
from app.core.config import settings

class SmartMoneyStrategy:
    """Very small proof-of-concept SmartMoney strategy based on SMA + ATR filter."""

    def __init__(self, fast: int = 20, slow: int = 50, atr_period: int = 14):
        self.fast = fast
        self.slow = slow
        self.atr_period = atr_period

    def generate_signals(self, candles: List[List[float]]) -> Dict[int, Signal]:
        # candles: [timestamp, open, high, low, close, volume]
        closes = [float(c[4]) for c in candles]
        highs = [float(c[2]) for c in candles]
        lows = [float(c[3]) for c in candles]

        signals: dict[int, Signal] = {}
        if len(closes) < self.slow + 2:
            return signals

        for idx in range(self.slow, len(closes)):
            fast_sma = mean(closes[idx - self.fast : idx])
            slow_sma = mean(closes[idx - self.slow : idx])
            cur = closes[idx - 1]
            prev = closes[idx - 2]

            # ATR simple calc
            trs = [max(h - l, abs(h - closes[i - 1]) if i > 0 else 0, abs(l - closes[i - 1]) if i > 0 else 0)
                   for i, (h, l) in enumerate(zip(highs, lows))]
            if len(trs) < self.atr_period:
                continue
            atr = mean(trs[-self.atr_period:])

            # signal logic
            if fast_sma > slow_sma and cur > prev and cur - prev > 0.2 * atr:
                signals[idx] = Signal(
                    symbol=settings.SYMBOL,
                    side="BUY",
                    entry=cur,
                    stop_loss=round(cur - 1.5 * atr, 2),
                    take_profit_1=round(cur + 2 * atr, 2),
                    reason="smart_money_long",
                )
            elif fast_sma < slow_sma and cur < prev and prev - cur > 0.2 * atr:
                signals[idx] = Signal(
                    symbol=settings.SYMBOL,
                    side="SELL",
                    entry=cur,
                    stop_loss=round(cur + 1.5 * atr, 2),
                    take_profit_1=round(cur - 2 * atr, 2),
                    reason="smart_money_short",
                )

        return signals
