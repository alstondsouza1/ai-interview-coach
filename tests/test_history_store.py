"""Tests for privacy-preserving local mock-interview history."""

from pathlib import Path

from src.history_store import (
    delete_all_history,
    list_mock_sessions,
    save_mock_session,
)
from src.models import MockInterviewSummary


def test_history_round_trip_and_delete(tmp_path: Path) -> None:
    database = tmp_path / "history.db"
    summary = MockInterviewSummary(
        overall_score=76,
        readiness_label="Nearly ready",
        category_scores={"Technical": 70, "Behavioral": 80, "Situational": 78},
        rubric_scores={
            "Structure": 80,
            "Specificity": 72,
            "Ownership": 78,
            "Impact": 70,
            "Clarity": 85,
        },
        strengths=["Consistently strong: Clarity."],
        weaknesses=["Needs the most attention: Impact."],
        completed_questions=10,
        total_questions=10,
        average_time_seconds=84,
    )

    save_mock_session("session-1", "Software Engineering Intern", summary, database)
    sessions = list_mock_sessions(database_path=database)

    assert len(sessions) == 1
    assert sessions[0]["overall_score"] == 76
    assert sessions[0]["category_scores"]["Behavioral"] == 80
    assert "answer" not in sessions[0]
    assert "resume" not in sessions[0]

    delete_all_history(database)
    assert list_mock_sessions(database_path=database) == []


def test_duplicate_session_id_replaces_record(tmp_path: Path) -> None:
    database = tmp_path / "history.db"
    first = _summary(60)
    second = _summary(85)

    save_mock_session("same-id", "Intern", first, database)
    save_mock_session("same-id", "Intern", second, database)

    sessions = list_mock_sessions(database_path=database)
    assert len(sessions) == 1
    assert sessions[0]["overall_score"] == 85


def _summary(score: int) -> MockInterviewSummary:
    return MockInterviewSummary(
        overall_score=score,
        readiness_label="Developing",
        category_scores={},
        rubric_scores={},
        strengths=[],
        weaknesses=[],
        completed_questions=10,
        total_questions=10,
        average_time_seconds=60,
    )
