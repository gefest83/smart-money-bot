from __future__ import annotations
from datetime import datetime
from typing import Optional
from app.models import Position, Trade, Signal


class Executor:
    def __init__(self):
        self.position: Optional[Position] = None
        self.in_position = False

    def process_signal(self, signal: Signal, amount: float = 1.0) -> bool:
        if self.in_position:
            return False
        # open a position
        pos = Position(
            symbol=signal.symbol,
            side=signal.side,
            entry=signal.entry,
            stop_loss=signal.stop_loss,
            amount=amount,
            remaining=amount,
            take_profit_1=signal.take_profit_1,
            take_profit_2=signal.take_profit_2,
            take_profit_3=signal.take_profit_3,
            opened_at=datetime.utcnow(),
        )
        self.position = pos
        self.in_position = True
        return True

    def update_price(self, price: float) -> list[Trade] | None:
        """
        Called on each new price tick (bar close). Returns list of Trade objects closed at this price (could be partial closes), or None.
        """
        if not self.in_position or self.position is None:
            return None
        closed_trades: list[Trade] = []
        pos = self.position

        # helpers for partial closes: fractions for TP1, TP2, TP3
        tp_fractions = [0.3, 0.3, 0.4]

        # BUY side checks
        if pos.side == "BUY":
            # TP3
            if pos.take_profit_3 is not None and pos.remaining > 0 and price >= pos.take_profit_3:
                amt = pos.remaining * tp_fractions[2]
                pnl = (pos.take_profit_3 - pos.entry) * amt
                trade = Trade(pos.symbol, pos.side, pos.entry, pos.take_profit_3, amt, pnl, "TP3", pos.opened_at, datetime.utcnow())
                closed_trades.append(trade)
                pos.remaining -= amt

            # TP2
            if pos.take_profit_2 is not None and pos.remaining > 0 and price >= pos.take_profit_2:
                amt = pos.remaining * tp_fractions[1]
                pnl = (pos.take_profit_2 - pos.entry) * amt
                trade = Trade(pos.symbol, pos.side, pos.entry, pos.take_profit_2, amt, pnl, "TP2", pos.opened_at, datetime.utcnow())
                closed_trades.append(trade)
                pos.remaining -= amt

            # TP1
            if pos.take_profit_1 is not None and pos.remaining > 0 and price >= pos.take_profit_1:
                amt = pos.remaining * tp_fractions[0]
                pnl = (pos.take_profit_1 - pos.entry) * amt
                trade = Trade(pos.symbol, pos.side, pos.entry, pos.take_profit_1, amt, pnl, "TP1", pos.opened_at, datetime.utcnow())
                closed_trades.append(trade)
                pos.remaining -= amt

            # Stop
            if pos.stop_loss is not None and pos.remaining > 0 and price <= pos.stop_loss:
                amt = pos.remaining
                pnl = (price - pos.entry) * amt
                trade = Trade(pos.symbol, pos.side, pos.entry, price, amt, pnl, "Stop Loss", pos.opened_at, datetime.utcnow())
                closed_trades.append(trade)
                pos.remaining = 0

        else:
            # SELL side (inverse checks)
            if pos.take_profit_3 is not None and pos.remaining > 0 and price <= pos.take_profit_3:
                amt = pos.remaining * tp_fractions[2]
                pnl = (pos.entry - pos.take_profit_3) * amt
                trade = Trade(pos.symbol, pos.side, pos.entry, pos.take_profit_3, amt, pnl, "TP3", pos.opened_at, datetime.utcnow())
                closed_trades.append(trade)
                pos.remaining -= amt

            if pos.take_profit_2 is not None and pos.remaining > 0 and price <= pos.take_profit_2:
                amt = pos.remaining * tp_fractions[1]
                pnl = (pos.entry - pos.take_profit_2) * amt
                trade = Trade(pos.symbol, pos.side, pos.entry, pos.take_profit_2, amt, pnl, "TP2", pos.opened_at, datetime.utcnow())
                closed_trades.append(trade)
                pos.remaining -= amt

            if pos.take_profit_1 is not None and pos.remaining > 0 and price <= pos.take_profit_1:
                amt = pos.remaining * tp_fractions[0]
                pnl = (pos.entry - pos.take_profit_1) * amt
                trade = Trade(pos.symbol, pos.side, pos.entry, pos.take_profit_1, amt, pnl, "TP1", pos.opened_at, datetime.utcnow())
                closed_trades.append(trade)
                pos.remaining -= amt

            # Stop
            if pos.stop_loss is not None and pos.remaining > 0 and price >= pos.stop_loss:
                amt = pos.remaining
                pnl = (pos.entry - price) * amt
                trade = Trade(pos.symbol, pos.side, pos.entry, price, amt, pnl, "Stop Loss", pos.opened_at, datetime.utcnow())
                closed_trades.append(trade)
                pos.remaining = 0

        # finalize closures
        if self.position and self.position.remaining is not None and self.position.remaining <= 0:
            # fully closed
            self._close()

        return closed_trades if closed_trades else None

    def close_position(self, price: float, reason: str = "Manual") -> Optional[Trade]:
        if not self.in_position or self.position is None:
            return None
        pos = self.position
        if pos.remaining is None:
            amt = pos.amount
        else:
            amt = pos.remaining
        if pos.side == "BUY":
            pnl = (price - pos.entry) * amt
        else:
            pnl = (pos.entry - price) * amt

        trade = Trade(
            symbol=pos.symbol,
            side=pos.side,
            entry=pos.entry,
            exit=price,
            amount=amt,
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
