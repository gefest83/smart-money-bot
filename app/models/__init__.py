from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Signal:
    symbol: str
    side: str
    entry: float
    stop_loss: float
    take_profit_1: Optional[float] = None
    take_profit_2: Optional[float] = None
    take_profit_3: Optional[float] = None
    reason: str = ""
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Position:
    symbol: str
    side: str
    entry: float
    stop_loss: float
    amount: float
    take_profit_1: Optional[float] = None
    take_profit_2: Optional[float] = None
    take_profit_3: Optional[float] = None
    opened_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Trade:
    symbol: str
    side: str
    entry: float
    exit: float
    amount: float
    pnl: float
    reason: str
    opened_at: datetime
    closed_at: datetime
