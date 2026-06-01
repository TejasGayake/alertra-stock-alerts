"""SQLite database layer for Alertra stock alert app."""

import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class Database:
    """Handles all database operations for Alertra."""

    SCHEMA_SQL = """
        CREATE TABLE IF NOT EXISTS watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS watchlist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            watchlist_id INTEGER,
            symbol TEXT NOT NULL,
            display_name TEXT,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY(watchlist_id) REFERENCES watchlists(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            condition TEXT NOT NULL,
            price REAL,
            message TEXT,
            triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS cooldown (
            symbol TEXT,
            condition TEXT,
            last_trigger INTEGER,
            PRIMARY KEY (symbol, condition)
        );
    """

    def __init__(self, db_path: str = "alertra.db") -> None:
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()

    def _connect(self) -> None:
        """Establish database connection with WAL mode and foreign keys."""
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")

    def _create_tables(self) -> None:
        """Create all tables if they don't exist."""
        self._conn.executescript(self.SCHEMA_SQL)

    def _execute(
        self, sql: str, params: tuple = (), *, fetch_one: bool = False, fetch_all: bool = False
    ) -> Any:
        """Execute a query with error handling and connection management."""
        try:
            cursor = self._conn.execute(sql, params)
            self._conn.commit()
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            return cursor
        except sqlite3.Error as exc:
            self._conn.rollback()
            raise RuntimeError(f"Database error: {exc}") from exc

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    # ------------------------------------------------------------------
    # Watchlists
    # ------------------------------------------------------------------

    def create_watchlist(self, name: str) -> int:
        """Create a new watchlist and return its id."""
        row = self._execute(
            "INSERT INTO watchlists (name) VALUES (?)",
            (name,),
            fetch_one=False,
        )
        return row.lastrowid

    def get_watchlists(self) -> List[Dict[str, Any]]:
        """Return all watchlists ordered by name."""
        rows = self._execute(
            "SELECT id, name, is_active, created_at FROM watchlists ORDER BY name",
            fetch_all=True,
        )
        return [dict(r) for r in rows]

    def get_active_watchlist(self) -> Optional[Dict[str, Any]]:
        """Return the currently active watchlist or None."""
        row = self._execute(
            "SELECT id, name, is_active, created_at FROM watchlists WHERE is_active = 1",
            fetch_one=True,
        )
        return dict(row) if row else None

    def set_active_watchlist(self, watchlist_id: int) -> None:
        """Set a single watchlist as active, deactivating all others."""
        self._execute("UPDATE watchlists SET is_active = 0 WHERE is_active = 1")
        self._execute(
            "UPDATE watchlists SET is_active = 1 WHERE id = ?",
            (watchlist_id,),
        )

    def delete_watchlist(self, watchlist_id: int) -> None:
        """Delete a watchlist and cascade-delete its items."""
        self._execute(
            "DELETE FROM watchlists WHERE id = ?",
            (watchlist_id,),
        )

    def rename_watchlist(self, watchlist_id: int, name: str) -> None:
        """Rename an existing watchlist."""
        self._execute(
            "UPDATE watchlists SET name = ? WHERE id = ?",
            (name, watchlist_id),
        )

    # ------------------------------------------------------------------
    # Watchlist items (symbols)
    # ------------------------------------------------------------------

    def add_symbol(
        self, watchlist_id: int, symbol: str, display_name: Optional[str] = None
    ) -> int:
        """Add a symbol to a watchlist and return the new item id."""
        max_order = self._execute(
            "SELECT COALESCE(MAX(sort_order), 0) FROM watchlist_items WHERE watchlist_id = ?",
            (watchlist_id,),
            fetch_one=True,
        )[0]
        row = self._execute(
            "INSERT INTO watchlist_items (watchlist_id, symbol, display_name, sort_order) "
            "VALUES (?, ?, ?, ?)",
            (watchlist_id, symbol, display_name, max_order + 1),
        )
        return row.lastrowid

    def remove_symbol(self, item_id: int) -> None:
        """Remove a symbol from a watchlist by item id."""
        self._execute(
            "DELETE FROM watchlist_items WHERE id = ?",
            (item_id,),
        )

    def get_symbols(self, watchlist_id: int) -> List[Dict[str, Any]]:
        """Return all symbols in a watchlist ordered by sort_order."""
        rows = self._execute(
            "SELECT id, watchlist_id, symbol, display_name, sort_order "
            "FROM watchlist_items WHERE watchlist_id = ? ORDER BY sort_order",
            (watchlist_id,),
            fetch_all=True,
        )
        return [dict(r) for r in rows]

    def reorder_symbols(self, watchlist_id: int, item_ids: List[int]) -> None:
        """Reorder symbols by updating sort_order to match the given id list."""
        for index, item_id in enumerate(item_ids):
            self._execute(
                "UPDATE watchlist_items SET sort_order = ? WHERE id = ? AND watchlist_id = ?",
                (index, item_id, watchlist_id),
            )

    # ------------------------------------------------------------------
    # Alerts
    # ------------------------------------------------------------------

    def save_alert(
        self, symbol: str, condition: str, price: float, message: str
    ) -> None:
        """Persist a triggered alert."""
        self._execute(
            "INSERT INTO alerts (symbol, condition, price, message) VALUES (?, ?, ?, ?)",
            (symbol, condition, price, message),
        )

    def get_alerts(
        self, limit: int = 100, unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Return recent alerts, optionally filtering to unread only."""
        sql = (
            "SELECT id, symbol, condition, price, message, triggered_at, is_read "
            "FROM alerts"
        )
        if unread_only:
            sql += " WHERE is_read = 0"
        sql += " ORDER BY triggered_at DESC LIMIT ?"
        rows = self._execute(sql, (limit,), fetch_all=True)
        return [dict(r) for r in rows]

    def mark_alert_read(self, alert_id: int) -> None:
        """Mark a single alert as read."""
        self._execute(
            "UPDATE alerts SET is_read = 1 WHERE id = ?",
            (alert_id,),
        )

    def clear_alerts(self) -> None:
        """Delete all alerts."""
        self._execute("DELETE FROM alerts")

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Return a setting value or the default if not found."""
        row = self._execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,),
            fetch_one=True,
        )
        return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        """Insert or update a setting."""
        self._execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    def get_all_settings(self) -> Dict[str, str]:
        """Return all settings as a dictionary."""
        rows = self._execute(
            "SELECT key, value FROM settings",
            fetch_all=True,
        )
        return {row["key"]: row["value"] for row in rows}

    # ------------------------------------------------------------------
    # Cooldown
    # ------------------------------------------------------------------

    def is_in_cooldown(
        self, symbol: str, condition: str, cooldown_seconds: int = 300
    ) -> bool:
        """Return True if the symbol+condition pair is still within cooldown."""
        row = self._execute(
            "SELECT last_trigger FROM cooldown WHERE symbol = ? AND condition = ?",
            (symbol, condition),
            fetch_one=True,
        )
        if row is None:
            return False
        return (time.time() - row["last_trigger"]) < cooldown_seconds

    def update_cooldown(self, symbol: str, condition: str) -> None:
        """Set or refresh the cooldown timestamp for a symbol+condition pair."""
        self._execute(
            "INSERT INTO cooldown (symbol, condition, last_trigger) VALUES (?, ?, ?) "
            "ON CONFLICT(symbol, condition) DO UPDATE SET last_trigger = excluded.last_trigger",
            (symbol, condition, int(time.time())),
        )

    def get_cooldown(self, symbol: str, condition: str) -> Optional[int]:
        """Return the last_trigger epoch for a symbol+condition pair, or None."""
        row = self._execute(
            "SELECT last_trigger FROM cooldown WHERE symbol = ? AND condition = ?",
            (symbol, condition),
            fetch_one=True,
        )
        return row["last_trigger"] if row else None
