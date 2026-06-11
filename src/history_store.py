"""Privacy-preserving SQLite storage for aggregate interview results."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.models import MockInterviewSummary

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "interview_history.db"


def initialize_database(database_path: Path = DEFAULT_DATABASE_PATH) -> None:
    """Create the local history table if it does not already exist."""

    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS mock_sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                role_title TEXT NOT NULL,
                overall_score INTEGER NOT NULL,
                readiness_label TEXT NOT NULL,
                completed_questions INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                average_time_seconds INTEGER NOT NULL,
                category_scores TEXT NOT NULL,
                rubric_scores TEXT NOT NULL,
                strengths TEXT NOT NULL,
                weaknesses TEXT NOT NULL
            )
            """
        )


def save_mock_session(
    session_id: str,
    role_title: str,
    summary: MockInterviewSummary,
    database_path: Path = DEFAULT_DATABASE_PATH,
) -> None:
    """Save aggregate results without storing resume text or interview answers."""

    if not session_id.strip():
        raise ValueError("A session ID is required.")
    initialize_database(database_path)
    values = asdict(summary)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO mock_sessions (
                session_id, created_at, role_title, overall_score,
                readiness_label, completed_questions, total_questions,
                average_time_seconds, category_scores, rubric_scores,
                strengths, weaknesses
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                datetime.now(timezone.utc).isoformat(),
                role_title,
                summary.overall_score,
                summary.readiness_label,
                summary.completed_questions,
                summary.total_questions,
                summary.average_time_seconds,
                json.dumps(values["category_scores"]),
                json.dumps(values["rubric_scores"]),
                json.dumps(values["strengths"]),
                json.dumps(values["weaknesses"]),
            ),
        )


def list_mock_sessions(
    limit: int = 50,
    database_path: Path = DEFAULT_DATABASE_PATH,
) -> list[dict[str, Any]]:
    """Return newest aggregate sessions first."""

    if not database_path.exists():
        return []
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT * FROM mock_sessions
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (max(1, min(limit, 500)),),
        ).fetchall()
    return [_deserialize_row(dict(row)) for row in rows]


def delete_all_history(database_path: Path = DEFAULT_DATABASE_PATH) -> None:
    """Delete every saved aggregate interview session."""

    if not database_path.exists():
        return
    with sqlite3.connect(database_path) as connection:
        connection.execute("DELETE FROM mock_sessions")


def _deserialize_row(row: dict[str, Any]) -> dict[str, Any]:
    for field in ("category_scores", "rubric_scores", "strengths", "weaknesses"):
        row[field] = json.loads(row[field])
    return row
