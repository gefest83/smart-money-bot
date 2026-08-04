from __future__ import annotations
from typing import Dict
from app.models import Signal

class SignalEngine:
    def __init__(self):
        self.signals: Dict[int, Signal] = {}

    def load_signals(self, signals: Dict[int, Signal]) -> None:
        self.signals = signals

    def get_signal(self, index: int) -> Signal | None:
        return self.signals.get(index)
