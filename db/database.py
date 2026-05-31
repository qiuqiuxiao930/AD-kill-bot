"""SQLite database for storing warnings, group settings, and whitelist."""

import sqlite3
from pathlib import Path
from typing import Optional

from loguru import logger


class Database:
    def __init__(self, db_path: str = "db/scamguard.db") -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        cur = self._conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS warnings (
                user_id   INTEGER NOT NULL,
                chat_id   INTEGER NOT NULL,
                count     INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, chat_id)
            );

            CREATE TABLE IF NOT EXISTS group_settings (
                chat_id   INTEGER PRIMARY KEY,
                enabled   INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS whitelist (
                user_id   INTEGER NOT NULL,
                chat_id   INTEGER NOT NULL,
                PRIMARY KEY (user_id, chat_id)
            );

            CREATE TABLE IF NOT EXISTS detection_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id     INTEGER NOT NULL,
                user_id     INTEGER NOT NULL,
                message_text TEXT,
                detection_type TEXT,
                confidence  REAL,
                action_taken TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        self._conn.commit()
        logger.debug("Database tables initialised")

    # ── warnings ──────────────────────────────────────────────
    def get_warnings(self, user_id: int, chat_id: int) -> int:
        row = self._conn.execute(
            "SELECT count FROM warnings WHERE user_id=? AND chat_id=?",
            (user_id, chat_id),
        ).fetchone()
        return row["count"] if row else 0

    def add_warning(self, user_id: int, chat_id: int) -> int:
        current = self.get_warnings(user_id, chat_id)
        new_count = current + 1
        self._conn.execute(
            """INSERT INTO warnings (user_id, chat_id, count) VALUES (?, ?, ?)
               ON CONFLICT(user_id, chat_id) DO UPDATE SET count=excluded.count""",
            (user_id, chat_id, new_count),
        )
        self._conn.commit()
        return new_count

    def reset_warnings(self, user_id: int, chat_id: int) -> None:
        self._conn.execute(
            "DELETE FROM warnings WHERE user_id=? AND chat_id=?",
            (user_id, chat_id),
        )
        self._conn.commit()

    # ── group settings ────────────────────────────────────────
    def is_enabled(self, chat_id: int) -> bool:
        row = self._conn.execute(
            "SELECT enabled FROM group_settings WHERE chat_id=?", (chat_id,)
        ).fetchone()
        return bool(row["enabled"]) if row else True  # enabled by default

    def set_enabled(self, chat_id: int, enabled: bool) -> None:
        self._conn.execute(
            """INSERT INTO group_settings (chat_id, enabled) VALUES (?, ?)
               ON CONFLICT(chat_id) DO UPDATE SET enabled=excluded.enabled""",
            (chat_id, int(enabled)),
        )
        self._conn.commit()

    # ── whitelist ─────────────────────────────────────────────
    def is_whitelisted(self, user_id: int, chat_id: int) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM whitelist WHERE user_id=? AND chat_id=?",
            (user_id, chat_id),
        ).fetchone()
        return row is not None

    def add_to_whitelist(self, user_id: int, chat_id: int) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO whitelist (user_id, chat_id) VALUES (?, ?)",
            (user_id, chat_id),
        )
        self._conn.commit()

    def remove_from_whitelist(self, user_id: int, chat_id: int) -> None:
        self._conn.execute(
            "DELETE FROM whitelist WHERE user_id=? AND chat_id=?",
            (user_id, chat_id),
        )
        self._conn.commit()

    # ── detection log ─────────────────────────────────────────
    def log_detection(
        self,
        chat_id: int,
        user_id: int,
        message_text: str,
        detection_type: str,
        confidence: float,
        action_taken: str,
    ) -> None:
        self._conn.execute(
            """INSERT INTO detection_log
               (chat_id, user_id, message_text, detection_type, confidence, action_taken)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (chat_id, user_id, message_text, detection_type, confidence, action_taken),
        )
        self._conn.commit()

    def get_stats(self, chat_id: int) -> dict:
        row = self._conn.execute(
            "SELECT COUNT(*) as total FROM detection_log WHERE chat_id=?",
            (chat_id,),
        ).fetchone()
        total = row["total"] if row else 0

        type_rows = self._conn.execute(
            """SELECT detection_type, COUNT(*) as cnt
               FROM detection_log WHERE chat_id=?
               GROUP BY detection_type""",
            (chat_id,),
        ).fetchall()
        by_type = {r["detection_type"]: r["cnt"] for r in type_rows}
        return {"total_detections": total, "by_type": by_type}

    # ── admin helpers ─────────────────────────────────────────
    def get_all_stats(self) -> Optional[dict]:
        row = self._conn.execute(
            "SELECT COUNT(*) as total FROM detection_log"
        ).fetchone()
        return {"total_detections": row["total"]} if row else None

    def close(self) -> None:
        self._conn.close()
