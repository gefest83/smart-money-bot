from __future__ import annotations
from app.core.config import settings

class RiskManager:
    def __init__(self):
        self.risk_percent = settings.RISK_PERCENT

    def position_size(self, balance: float, entry_price: float, stop_loss: float) -> float:
        # very basic: risk_percent of balance divided by dollar distance to stop
        risk_amount = balance * (self.risk_percent / 100.0)
        distance = abs(entry_price - stop_loss)
        if distance <= 0:
            return 0.0
        return risk_amount / distance
