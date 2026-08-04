from __future__ import annotations
from typing import Sequence


def simple_pivots(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    window: int = 5,
):
    pivots = []
    n = len(closes)
    for i in range(window, n - window):
        high_window = max(highs[i - window : i + window + 1])
        low_window = min(lows[i - window : i + window + 1])
        if highs[i] == high_window:
            pivots.append((i, "resistance", highs[i]))
        elif lows[i] == low_window:
            pivots.append((i, "support", lows[i]))
    return pivots
