from __future__ import annotations
from statistics import pstdev
from typing import Sequence

def volatility(closes: Sequence[float], period: int = 20) -> list[float]:
    if len(closes) < period:
        return []
    vols: list[float] = []
    for i in range(period, len(closes) + 1):
        window = closes[i - period : i]
        vols.append(pstdev(window))
    return vols
