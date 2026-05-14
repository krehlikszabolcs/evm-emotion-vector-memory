from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path((BASE_DIR / "DATA")).resolve()
SQLITE_DIR = DATA_DIR / "sqlite"
LOGS_DIR = DATA_DIR / "logs"
DB_PATH = SQLITE_DIR / "evm.sqlite3"


def ensure_runtime_dirs() -> None:
    SQLITE_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def connect() -> sqlite3.Connection:
    ensure_runtime_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def append_jsonl(name: str, payload: Dict[str, Any]) -> None:
    ensure_runtime_dirs()
    path = LOGS_DIR / name
    record = dict(payload)
    record.setdefault("mirrored_at", utc_now_iso())
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def safe_append_jsonl(name: str, payload: Dict[str, Any]) -> None:
    try:
        append_jsonl(name, payload)
    except Exception:
        # Mirror logs are best-effort only. SQLite remains the source of truth.
        pass


def init_db() -> None:
    ensure_runtime_dirs()
    with connect() as conn:
        conn.executescript(
            """
            PRAGMA journal_mode=WAL;

            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                response_model TEXT NOT NULL,
                extractor_model TEXT NOT NULL,
                previous_response_id TEXT,
                pev_json TEXT NOT NULL,
                eev_json TEXT NOT NULL,
                fev_lower_json TEXT NOT NULL,
                fev_upper_json TEXT NOT NULL,
                fev_center_json TEXT NOT NULL,
                boundary_counts_json TEXT NOT NULL,
                last_identity_hash TEXT
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                openai_response_id TEXT,
                FOREIGN KEY(chat_id) REFERENCES chats(id)
            );

            CREATE TABLE IF NOT EXISTS ev_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                turn_index INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                entry_json TEXT NOT NULL,
                exit_json TEXT NOT NULL,
                ev_json TEXT NOT NULL,
                extractor_version_id TEXT NOT NULL,
                extractor_config_hash TEXT NOT NULL,
                extraction_timestamp TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY(chat_id) REFERENCES chats(id)
            );

            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                pev_json TEXT NOT NULL,
                eev_json TEXT NOT NULL,
                fev_center_json TEXT NOT NULL,
                stability_json TEXT NOT NULL,
                fev_compliance_score REAL NOT NULL,
                cis_json TEXT NOT NULL,
                FOREIGN KEY(chat_id) REFERENCES chats(id)
            );

            CREATE TABLE IF NOT EXISTS index_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                created_at TEXT NOT NULL,
                category TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                FOREIGN KEY(chat_id) REFERENCES chats(id)
            );

            CREATE INDEX IF NOT EXISTS idx_messages_chat_created ON messages(chat_id, created_at);
            CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);
            CREATE INDEX IF NOT EXISTS idx_ev_records_chat_turn ON ev_records(chat_id, turn_index);
            CREATE INDEX IF NOT EXISTS idx_ev_records_created ON ev_records(created_at);
            CREATE INDEX IF NOT EXISTS idx_snapshots_chat_created ON snapshots(chat_id, created_at);
            CREATE INDEX IF NOT EXISTS idx_index_log_chat_category_created ON index_log(chat_id, category, created_at);
            CREATE INDEX IF NOT EXISTS idx_index_log_category_created ON index_log(category, created_at);
            """
        )


def fetch_all(query: str, params: tuple = ()) -> List[sqlite3.Row]:
    with connect() as conn:
        cur = conn.execute(query, params)
        return cur.fetchall()


def fetch_one(query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
    with connect() as conn:
        cur = conn.execute(query, params)
        return cur.fetchone()


def execute(query: str, params: tuple = ()) -> int:
    with connect() as conn:
        cur = conn.execute(query, params)
        conn.commit()
        return int(cur.lastrowid)


def execute_many(query: str, params_seq) -> None:
    with connect() as conn:
        conn.executemany(query, params_seq)
        conn.commit()


def dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def loads(text: str) -> Any:
    return json.loads(text)


def row_to_chat_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "response_model": row["response_model"],
        "extractor_model": row["extractor_model"],
        "previous_response_id": row["previous_response_id"],
        "pev": loads(row["pev_json"]),
        "eev": loads(row["eev_json"]),
        "fev_lower": loads(row["fev_lower_json"]),
        "fev_upper": loads(row["fev_upper_json"]),
        "fev_center": loads(row["fev_center_json"]),
        "boundary_counts": loads(row["boundary_counts_json"]),
        "last_identity_hash": row["last_identity_hash"],
    }
