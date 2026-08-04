from __future__ import annotations
import csv
from pathlib import Path
from typing import Iterable
from app.models import Trade


class BacktestReport:
    def __init__(self, out_dir: Path | str = "reports"):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def save(self, trades: Iterable[Trade]) -> str:
        path = self.out_dir / "trades_report.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "symbol", "side", "entry", "exit", "amount", "pnl", "reason",
                "opened_at", "closed_at",
            ])
            for t in trades:
                writer.writerow([
                    t.symbol,
                    t.side,
                    t.entry,
                    t.exit,
                    t.amount,
                    t.pnl,
                    t.reason,
                    t.opened_at.isoformat() if hasattr(t.opened_at, 'isoformat') else t.opened_at,
                    t.closed_at.isoformat() if hasattr(t.closed_at, 'isoformat') else t.closed_at,
                ])
        return str(path)
