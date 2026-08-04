from __future__ import annotations
from datetime import datetime
from typing import Optional
from app.models import Position, Trade, Signal

class Executor:
    def __init__(self):
        self.position: Optional[Position] = None
        self.in_position = False

    def process_signal(self, signal: Signal) -> bool:
        if self.in_position:
            return False
        # open a position
        amount = 1.0  # placeholder; risk manager should set real amount
        self.position = Position(
            symbol=signal.symbol,
            side=signal.side,
            entry=signal.entry,
            stop_loss=signal.stop_loss,
            amount=amount,
            opened_at=datetime.utcnow(),
        )
        self.in_position = True
        return True

    def update_price(self, price: float) -> Optional[Trade]:
        if not self.in_position or self.position is None:
            return None
        # check stop or take profit (very simple immediate exit logic placeholder)
        pos = self.position
        if pos.side == "BUY":
            if price <= pos.stop_loss:
                trade = Trade(
                    symbol=pos.symbol,
                    side=pos.side,
                    entry=pos.entry,
                    exit=price,
                    amount=pos.amount,
                    pnl=(price - pos.entry) * pos.amount,
                    reason="Stop Loss",
                    opened_at=pos.opened_at,
                    closed_at=datetime.utcnow(),
                )
                self._close()
                return trade
        else:
            if price >= pos.stop_loss:
                trade = Trade(
                    symbol=pos.symbol,
                    side=pos.side,
                    entry=pos.entry,
                    exit=price,
                    amount=pos.amount,
                    pnl=(pos.entry - price) * pos.amount,
                    reason="Stop Loss",
                    opened_at=pos.opened_at,
                    closed_at=datetime.utcnow(),
                )
                self._close()
                return trade
        return None

    def close_position(self, price: float, reason: str = "Manual") -> Optional[Trade]:
        if not self.in_position or self.position is None:
            return None
        pos = self.position
        if pos.side == "BUY":
            pnl = (price - pos.entry) * pos.amount
        else:
            pnl = (pos.entry - price) * pos.amount

        trade = Trade(
            symbol=pos.symbol,
            side=pos.side,
            entry=pos.entry,
            exit=price,
            amount=pos.amount,
            pnl=pnl,
            reason=reason,
            opened_at=pos.opened_at,
            closed_at=datetime.utcnow(),
        )
        self._close()
        return trade

    def _close(self):
        self.position = None
        self.in_position = False
