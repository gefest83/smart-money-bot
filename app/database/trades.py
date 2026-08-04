from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from collections.abc import Mapping

from app.core.logger import logger


class TradeDatabase:

    def __init__(self, path="data/trades.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Try to open existing database; if it's corrupted or not a DB file,
        # recreate a fresh database file to avoid crashes during tests or startup.
        try:
            self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
            try:
                self.create_table()
            except sqlite3.DatabaseError:
                logger.warning("Trade database file is invalid or corrupted, recreating.")
                try:
                    self.conn.close()
                except Exception:
                    pass
                try:
                    # remove the invalid file and create a new database
                    self.path.unlink(missing_ok=True)
                except Exception:
                    logger.exception("Failed to remove invalid trade DB file")
                self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
                self.create_table()

        except sqlite3.DatabaseError:
            # In case connection itself failed, attempt to recreate the file
            logger.warning("Failed to open trade database, creating a new one.")
            try:
                self.path.unlink(missing_ok=True)
            except Exception:
                logger.exception("Failed to remove trade DB file during recovery")
            self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
            self.create_table()

        logger.info(f"Trade database ready: {self.path}")

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            side TEXT,
            entry REAL,
            exit REAL,
            amount REAL,
            pnl REAL,
            reason TEXT,
            opened_at TEXT,
            closed_at TEXT
        )
        """

        self.conn.execute(query)
        self.conn.commit()

    def _field(self, trade, field_name):
        if isinstance(trade, Mapping):
            value = trade[field_name]
        else:
            value = getattr(trade, field_name)

        if isinstance(value, datetime):
            return value.isoformat()

        return value

    def add_trade(self, trade):
        query = """
        INSERT INTO trades (
            symbol,
            side,
            entry,
            exit,
            amount,
            pnl,
            reason,
            opened_at,
            closed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        self.conn.execute(
            query,
            (
                self._field(trade, "symbol"),
                self._field(trade, "side"),
                self._field(trade, "entry"),
                self._field(trade, "exit"),
                self._field(trade, "amount"),
                self._field(trade, "pnl"),
                self._field(trade, "reason"),
                self._field(trade, "opened_at"),
                self._field(trade, "closed_at"),
            ),
        )
        self.conn.commit()

    def get_trades(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM trades ORDER BY id DESC")
        return cursor.fetchall()

    def get_all_trades(self):
        return self.get_trades()