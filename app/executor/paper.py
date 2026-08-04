from __future__ import annotations
from datetime import datetime
from typing import Optional

from app.executor.base import BaseExecutor
from app.core.config import settings
from app.core.logger import logger
from app.models import Position, Trade


class PaperExecutor(BaseExecutor):

    def __init__(self, balance: Optional[float] = None):
        self.balance = (
            balance
            if balance is not None
            else settings.PAPER_BALANCE
        )
        self.position: Optional[Position] = None
        self.history: list[Trade] = []

    @property
    def in_position(self) -> bool:
        return self.position is not None

    def open_position(
        self,
        symbol: str,
        side: str,
        entry: float,
        stop_loss: float,
        take_profit_1: Optional[float] = None,
        take_profit_2: Optional[float] = None,
        take_profit_3: Optional[float] = None,
        amount: float = 0.0,
    ) -> bool:
        if self.in_position:
            logger.warning("Позиция уже открыта")
            return False

        if amount <= 0:
            logger.warning(
                "Невозможно открыть позицию с нулевым размером"
            )
            return False

        self.position = Position(
            symbol=symbol,
            side=side,
            entry=entry,
            stop_loss=stop_loss,
            amount=amount,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            take_profit_3=take_profit_3,
        )

        logger.success(
            f"Открыта бумажная позиция {side} {symbol} "
            f"по {entry:.2f} с размером {amount:.8f}"
        )

        return True

    def close_position(
        self,
        price: float,
        reason: str = "Закрытие позиции",
    ):
        if not self.in_position:
            logger.warning("Нет открытой позиции для закрытия")
            return None

        closed_trade = self._build_trade(
            exit_price=price,
            reason=reason,
        )

        self.history.append(closed_trade)
        self.position = None
        self._apply_pnl(closed_trade.pnl)

        logger.success(
            f"Закрыта бумажная позиция {closed_trade.side} "
            f"{closed_trade.symbol} по {price:.2f}. PnL={closed_trade.pnl:.2f}"
        )

        return closed_trade

    def update(self, price: float):
        if not self.in_position:
            return None

        position = self.position
        take_profit = position.take_profit_1

        if position.side == "BUY":
            if price <= position.stop_loss:
                return self.close_position(
                    price,
                    reason="Stop Loss",
                )

            if take_profit is not None and price >= take_profit:
                return self.close_position(
                    price,
                    reason="Take Profit",
                )

        if position.side == "SELL":
            if price >= position.stop_loss:
                return self.close_position(
                    price,
                    reason="Stop Loss",
                )

            if take_profit is not None and price <= take_profit:
                return self.close_position(
                    price,
                    reason="Take Profit",
                )

        return None

    def _build_trade(
        self,
        exit_price: float,
        reason: str,
    ) -> Trade:
        assert self.position is not None

        pnl = self._calculate_pnl(
            exit_price=exit_price,
        )

        return Trade(
            symbol=self.position.symbol,
            side=self.position.side,
            entry=self.position.entry,
            exit=exit_price,
            amount=self.position.amount,
            pnl=pnl,
            reason=reason,
            opened_at=self.position.opened_at,
            closed_at=datetime.utcnow(),
        )

    def _calculate_pnl(self, exit_price: float) -> float:
        assert self.position is not None

        if self.position.side == "BUY":
            return (exit_price - self.position.entry) * self.position.amount

        return (self.position.entry - exit_price) * self.position.amount

    def _apply_pnl(self, pnl: float) -> None:
        self.balance += pnl
        logger.info(f"Баланс после сделки: {self.balance:.2f}")
