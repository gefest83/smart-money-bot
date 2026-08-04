from __future__ import annotations
from typing import Sequence

def atr(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], period: int = 14) -> list[float]:
    if not (len(highs) == len(lows) == len(closes)):
        raise ValueError("Input series must have equal length")

    trs: list[float] = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        trs.append(tr)

    atrs: list[float] = []
    if len(trs) < period:
        return atrs

    # simple moving average of TR for ATR
    for i in range(period - 1, len(trs)):
        window = trs[i - (period - 1) : i + 1]
        atrs.append(sum(window) / period)

    # pad to align with input length (leading Nones omitted)
    return atrs
