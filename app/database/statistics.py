from app.core.logger import logger


class TradeStatistics:

    def __init__(self, database):

        self.database = database


    def calculate(self):

        trades = self.database.get_all_trades()


        if not trades:

            logger.warning(
                "Нет сделок для анализа"
            )

            return None


        total = len(trades)

        wins = 0
        losses = 0

        profit = 0


        for t in trades:

            pnl = t[6]

            profit += pnl

            if pnl > 0:
                wins += 1
            else:
                losses += 1


        winrate = (
            wins / total * 100
            if total
            else 0
        )


        logger.info(
            f"""
================ STATISTICS ================

Trades:
{total}

Wins:
{wins}

Losses:
{losses}

Winrate:
{winrate:.2f} %

Profit:
{profit:.2f} USDT

===========================================
"""
        )


        return {
            "trades": total,
            "wins": wins,
            "losses": losses,
            "winrate": winrate,
            "profit": profit
        }