from loguru import logger


class LiveExecutor:
    """
    Реальный исполнитель через CCXT.

    По умолчанию безопасный режим:
    ENABLE_LIVE_ORDERS = False
    """


    def __init__(
        self,
        exchange,
        enabled=False,
    ):

        self.exchange = exchange

        self.enabled = enabled

        self.position = None


        logger.info(
            f"""
=============== LIVE EXECUTOR ================

Status:
{"ACTIVE" if enabled else "SAFE MODE"}

Real Orders:
{"ENABLED" if enabled else "DISABLED"}

===============================================
"""
        )


    @property
    def in_position(self):

        return self.position is not None


    def open_position(
        self,
        signal,
        amount,
    ):


        side = (
            "buy"
            if signal.side == "BUY"
            else "sell"
        )


        order_data = {

            "symbol":
                signal.symbol,

            "side":
                side,

            "amount":
                amount,

            "type":
                "market",

        }


        logger.info(
            f"""
=============== LIVE ORDER =================

Symbol:
{signal.symbol}

Side:
{side}

Amount:
{amount}

=============================================
"""
        )


        if not self.enabled:


            logger.warning(
                "LIVE ордер заблокирован. Safe mode."
            )


            return False


        try:


            order = self.exchange.create_order(

                symbol=signal.symbol,

                type="market",

                side=side,

                amount=amount,

            )


            self.position = order


            logger.success(
                "LIVE ORDER EXECUTED"
            )


            return True


        except Exception as e:


            logger.error(
                f"LIVE ORDER ERROR: {e}"
            )


            return False


    def close_position(
        self,
        symbol,
        amount,
        side,
    ):


        if not self.enabled:

            logger.warning(
                "LIVE CLOSE заблокирован. Safe mode."
            )

            return False


        close_side = (

            "sell"
            if side == "BUY"
            else "buy"

        )


        try:


            order = self.exchange.create_order(

                symbol=symbol,

                type="market",

                side=close_side,

                amount=amount,

            )


            self.position = None


            logger.success(
                "LIVE POSITION CLOSED"
            )


            return order


        except Exception as e:


            logger.error(
                f"LIVE CLOSE ERROR: {e}"
            )


            return False


    def update(
        self,
        price,
    ):

        return


    def get_position(self):

        return self.position