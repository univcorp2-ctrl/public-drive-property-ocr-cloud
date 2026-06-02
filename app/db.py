import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.config import get_settings


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    settings = get_settings()
    settings.app_data_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                note_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                token TEXT NOT NULL,
                note_id TEXT NOT NULL,
                upload_name TEXT NOT NULL,
                extracted_text TEXT NOT NULL,
                result_json TEXT NOT NULL,
                output_dir TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def create_session(token: str, note_id: str) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO sessions(token, note_id, created_at) VALUES (?, ?, ?)",
            (token, note_id, utc_now()),
        )


def get_session(token: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE token = ?", (token,)).fetchone()
        return dict(row) if row else None


def create_job(
    job_id: str,
    token: str,
    note_id: str,
    upload_name: str,
    extracted_text: str,
    result: dict[str, Any],
    output_dir: Path,
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO jobs(
                job_id, token, note_id, upload_name, extracted_text,
                result_json, output_dir, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                token,
                note_id,
                upload_name,
                extracted_text,
                json.dumps(result, ensure_ascii=False),
                str(output_dir),
                utc_now(),
            ),
        )


def get_job(job_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        if row is None:
            return None
        data = dict(row)
        data["result"] = json.loads(data.pop("result_json"))
        return data
