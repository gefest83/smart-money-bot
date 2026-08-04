import time

from app.core.logger import logger


class PositionMonitor:
    """
    Следит за открытой позицией и автоматически
    закрывает её по Stop Loss или Take Profit.
    """

    def __init__(
        self,
        executor,
        exchange,
        interval=10,
    ):
        self.executor = executor
        self.exchange = exchange
        self.interval = interval

        logger.info(
            f"Position Monitor запущен. Интервал: {interval} сек."
        )

    def run(self):

        while True:

            status = self.executor.status()
            position = status["position"]

            if position is None:
                logger.success("Позиция закрыта.")
                break

            ticker = self.exchange.fetch_ticker(
                position.symbol
            )

            price = ticker["last"]

            logger.info(
                f"""
================ POSITION ================

Symbol : {position.symbol}
Side   : {position.side}

Entry  : {position.entry}
Price  : {price}

SL     : {position.stop_loss}
TP1    : {position.take_profit_1}
TP2    : {position.take_profit_2}
TP3    : {position.take_profit_3}

==========================================
"""
            )

            # Передаем цену PaperExecutor
            self.executor.update_price(price)

            time.sleep(self.interval)