import sqlite3
import uuid
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_agent TEXT,
    ip_address TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER DEFAULT 0,
    model TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(last_active);
"""


_DB_PATH: Optional[str] = None


def init_db(db_path: str) -> None:
    global _DB_PATH
    _DB_PATH = db_path
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    logger.info(f"📁 Database initialized at {db_path}")


@contextmanager
def get_connection():
    if _DB_PATH is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()

def create_session(user_agent: str = "", ip_address: str = "") -> str:
    session_id = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO sessions (id, user_agent, ip_address) VALUES (?, ?, ?)",
            (session_id, user_agent, ip_address),
        )
        conn.commit()
    logger.debug(f"🆕 Created session {session_id}")
    return session_id


def touch_session(session_id: str) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE sessions SET last_active = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,),
        )
        conn.commit()
        return cur.rowcount > 0


def session_exists(session_id: str) -> bool:
    with get_connection() as conn:
        cur = conn.execute("SELECT 1 FROM sessions WHERE id = ?", (session_id,))
        return cur.fetchone() is not None


def is_session_expired(session_id: str, timeout_minutes: int) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT last_active FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if row is None:
            return True
        last = datetime.fromisoformat(row["last_active"])
        return datetime.utcnow() - last > timedelta(minutes=timeout_minutes)


def add_message(
    session_id: str,
    role: str,
    content: str,
    tokens_used: int = 0,
    model: str = "",
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO messages (session_id, role, content, tokens_used, model)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, role, content, tokens_used, model),
        )
        conn.commit()
        return cur.lastrowid


def get_messages(session_id: str, limit: int = 50) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT role, content, created_at FROM messages
               WHERE session_id = ?
               ORDER BY id ASC
               LIMIT ?""",
            (session_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]


def clear_session_messages(session_id: str) -> int:
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.commit()
        return cur.rowcount


def get_stats() -> dict:
    with get_connection() as conn:
        total_sessions = conn.execute("SELECT COUNT(*) as c FROM sessions").fetchone()["c"]
        total_messages = conn.execute("SELECT COUNT(*) as c FROM messages").fetchone()["c"]
        active_24h = conn.execute(
            "SELECT COUNT(*) as c FROM sessions WHERE last_active > datetime('now', '-1 day')"
        ).fetchone()["c"]
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "active_sessions_24h": active_24h,
        }
