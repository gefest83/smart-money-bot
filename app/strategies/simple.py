from __future__ import annotations
from statistics import mean
from typing import Dict

from app.core.config import settings
from app.models import Signal


class SimpleStrategy:
    """
    Простая стратегия на основе скользящих средних.

    Для каждого бара она генерирует сигналы входа на основе
    перекрестия короткой и длинной SMA.
    """

    def __init__(self):
        self.fast_period = 20
        self.slow_period = 50

    def generate_signals(
        self,
        candles: list[list[float]],
    ) -> Dict[int, Signal]:
        closes = [float(candle[4]) for candle in candles]
        signals: dict[int, Signal] = {}

        for index in range(self.slow_period, len(closes)):
            fast_sma = mean(closes[index - self.fast_period:index])
            slow_sma = mean(closes[index - self.slow_period:index])
            current_close = closes[index - 1]
            previous_close = closes[index - 2]

            if fast_sma > slow_sma and current_close > previous_close:
                entry = current_close
                stop_loss = round(entry * 0.995, 2)
                take_profit = round(entry * 1.010, 2)
                signals[index] = Signal(
                    symbol=settings.SYMBOL,
                    side="BUY",
                    entry=entry,
                    stop_loss=stop_loss,
                    take_profit_1=take_profit,
                    reason="SMA crossover BUY",
                )

            if fast_sma < slow_sma and current_close < previous_close:
                entry = current_close
                stop_loss = round(entry * 1.005, 2)
                take_profit = round(entry * 0.990, 2)
                signals[index] = Signal(
                    symbol=settings.SYMBOL,
                    side="SELL",
                    entry=entry,
                    stop_loss=stop_loss,
                    take_profit_1=take_profit,
                    reason="SMA crossover SELL",
                )

        return signals
