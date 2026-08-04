from app.executor.paper import PaperExecutor
from app.risk.manager import RiskManager
from app.core.logger import logger


class ExecutorManager:

    def __init__(self, exchange=None, risk=None):
        self.exchange = exchange
        self.risk = risk or RiskManager()

        self.executor = PaperExecutor()

        logger.info(
            """
================ EXECUTOR ================

Mode:
PAPER

==========================================
"""
        )

    @property
    def position(self):
        return self.executor.position

    @property
    def in_position(self):
        return self.executor.in_position

    @property
    def balance(self):
        return self.executor.balance

    def process_signal(self, signal):

        if self.executor.position is not None:
            return False


        amount = self.risk.calculate_position_size(
            balance=self.executor.balance,
            entry=signal.entry,
            stop_loss=signal.stop_loss
        )


        return self.executor.open_position(
            symbol=signal.symbol,
            side=signal.side,
            entry=signal.entry,
            stop_loss=signal.stop_loss,
            take_profit_1=signal.take_profit_1,
            take_profit_2=signal.take_profit_2,
            take_profit_3=signal.take_profit_3,
            amount=amount
        )


    def update_price(self, price):

        if price is None:
            return None

        return self.executor.update(price)


    def status(self):

        return {
            "balance": self.executor.balance,
            "position": self.executor.position
        }