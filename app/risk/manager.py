from typing import Optional

from app.core.config import settings


class RiskManager:

    def __init__(
        self,
        leverage: Optional[float] = None,
        risk_percent: Optional[float] = None,
    ):
        self.leverage = (
            leverage
            if leverage is not None
            else settings.LEVERAGE
        )
        self.risk_percent = (
            risk_percent
            if risk_percent is not None
            else settings.RISK_PERCENT
        )

    def calculate_position_size(
        self,
        balance: float,
        entry: float,
        stop_loss: float,
    ) -> float:
        if balance <= 0:
            return 0.0

        if entry == stop_loss:
            return 0.0

        risk_amount = balance * self.risk_percent / 100.0
        price_distance = abs(entry - stop_loss)

        if price_distance == 0:
            return 0.0

        quantity = (risk_amount * self.leverage) / price_distance

        return round(max(quantity, 0.0), 8)
