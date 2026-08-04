from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
import csv


class BacktestReport:

    def __init__(self):
        self.output = Path("reports")
        self.output.mkdir(exist_ok=True, parents=True)

    def _serialize(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    def _field(self, trade, field_name):
        if isinstance(trade, Mapping):
            return self._serialize(trade[field_name])
        return self._serialize(getattr(trade, field_name))

    def save(self, history):
        file = self.output / "trades.csv"

        with open(file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Symbol",
                "Side",
                "Entry",
                "Exit",
                "PnL",
                "Reason",
                "Opened",
                "Closed",
            ])

            for trade in history:
                writer.writerow([
                    self._field(trade, "symbol"),
                    self._field(trade, "side"),
                    self._field(trade, "entry"),
                    self._field(trade, "exit"),
                    self._field(trade, "pnl"),
                    self._field(trade, "reason"),
                    self._field(trade, "opened_at"),
                    self._field(trade, "closed_at"),
                ])

        return file
