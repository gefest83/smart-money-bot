from __future__ import annotations
from typing import Dict, List, Optional
from statistics import mean

from app.models import Signal
from app.core.config import settings


def _atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
    trs: List[float] = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        trs.append(tr)
    atrs: List[float] = []
    if len(trs) < period:
        return atrs
    # simple moving average of TR
    for i in range(period - 1, len(trs)):
        window = trs[i - (period - 1) : i + 1]
        atrs.append(sum(window) / period)
    # pad to align with input (atr for bar index i corresponds to i+1 in closes)
    # we'll return atrs aligned to closes[period:]
    return atrs


class SmartMoneyStrategy:
    """
    Port of the TradingView Pine Script Smart Money Trades Pro (BOSWaves) — simplified deterministic version.

    Behavior:
    - Detect pivot highs/lows using symmetric lookback `structure_period`.
    - When a pivot is found, wait for a break (by body or wick) to trigger an entry at pivot price.
    - Calculate ATR-based dynamic range for TP/SL levels using volatility_multiplier.
    - Emit a Signal at the bar where the break occurs, with stop/tp levels attached.
    """

    def __init__(self, structure_period: int = 20, confirmation: str = "Body", volatility_multiplier: float = 2.0, atr_period: int = 14):
        self.structure_period = max(5, min(50, structure_period))
        self.confirmation = confirmation  # "Body" or "Wick"
        self.volatility_multiplier = volatility_multiplier
        self.atr_period = atr_period

    def _pivots(self, highs: List[float], lows: List[float]) -> (List[Optional[int]], List[Optional[int]]):
        n = len(highs)
        left = right = self.structure_period
        pivot_highs: List[Optional[int]] = [None] * n
        pivot_lows: List[Optional[int]] = [None] * n
        for i in range(left, n - right):
            window_h = highs[i - left : i + right + 1]
            window_l = lows[i - left : i + right + 1]
            if highs[i] == max(window_h):
                pivot_highs[i] = i
            if lows[i] == min(window_l):
                pivot_lows[i] = i
        return pivot_highs, pivot_lows

    def generate_signals(self, candles: List[List[float]]) -> Dict[int, Signal]:
        # candles: [timestamp, open, high, low, close, volume]
        n = len(candles)
        if n < self.structure_period + self.atr_period + 2:
            return {}

        highs = [float(c[2]) for c in candles]
        lows = [float(c[3]) for c in candles]
        closes = [float(c[4]) for c in candles]

        pivot_highs, pivot_lows = self._pivots(highs, lows)

        # precompute ATR aligned roughly to closes index
        atr_series = _atr(highs, lows, closes, period=self.atr_period)
        # atr_series corresponds to trs window starting at index self.atr_period in closes
        signals: Dict[int, Signal] = {}

        last_high = None
        last_low = None
        last_high_bar = None
        last_low_bar = None

        # iterate bars and record pivots, then watch for breakouts
        for i in range(n):
            # detect pivot registration
            if pivot_highs[i] is not None:
                last_high = highs[i]
                last_high_bar = i
            if pivot_lows[i] is not None:
                last_low = lows[i]
                last_low_bar = i

            # check for break after pivots
            if last_high is not None:
                # break condition: body or wick
                broken = False
                if self.confirmation == "Body":
                    if closes[i] > last_high:
                        broken = True
                else:
                    if highs[i] > last_high:
                        broken = True
                if broken:
                    # compute ATR at this bar index (use nearest available)
                    atr_idx = i - (self.atr_period)
                    atr_value = None
                    if atr_idx >= 0 and atr_idx < len(atr_series):
                        atr_value = atr_series[atr_idx]
                    else:
                        # fallback to simple range
                        atr_value = max(0.0, highs[i] - lows[i])

                    entry = float(last_high)
                    tr = atr_value * self.volatility_multiplier
                    tp1 = round(entry + tr * 0.8, 8)
                    tp2 = round(entry + tr * 1.6, 8)
                    tp3 = round(entry + tr * 2.8, 8)
                    stop = round(entry - tr * 1.2, 8)
                    signals[i] = Signal(
                        symbol=settings.SYMBOL,
                        side="BUY",
                        entry=entry,
                        stop_loss=stop,
                        take_profit_1=tp1,
                        take_profit_2=tp2,
                        take_profit_3=tp3,
                        reason="smart_money_break_bull",
                    )
                    # clear last_high to wait for next pivot
                    last_high = None
                    last_high_bar = None

            if last_low is not None:
                broken = False
                if self.confirmation == "Body":
                    if closes[i] < last_low:
                        broken = True
                else:
                    if lows[i] < last_low:
                        broken = True
                if broken:
                    atr_idx = i - (self.atr_period)
                    atr_value = None
                    if atr_idx >= 0 and atr_idx < len(atr_series):
                        atr_value = atr_series[atr_idx]
                    else:
                        atr_value = max(0.0, highs[i] - lows[i])

                    entry = float(last_low)
                    tr = atr_value * self.volatility_multiplier
                    tp1 = round(entry - tr * 0.8, 8)
                    tp2 = round(entry - tr * 1.6, 8)
                    tp3 = round(entry - tr * 2.8, 8)
                    stop = round(entry + tr * 1.2, 8)
                    signals[i] = Signal(
                        symbol=settings.SYMBOL,
                        side="SELL",
                        entry=entry,
                        stop_loss=stop,
                        take_profit_1=tp1,
                        take_profit_2=tp2,
                        take_profit_3=tp3,
                        reason="smart_money_break_bear",
                    )
                    last_low = None
                    last_low_bar = None

        return signals
