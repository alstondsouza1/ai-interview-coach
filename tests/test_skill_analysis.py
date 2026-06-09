"""Tests for deterministic skill extraction and matching."""

from src.skill_analysis import (
    classify_job_skills,
    compare_skills,
    extract_skill_evidence,
    extract_skills,
)


def test_extract_skills_handles_aliases_and_avoids_substrings() -> None:
    text = "Built RESTful APIs with Python and React.js. Used GitHub."

    assert extract_skills(text) == ["Git", "Python", "React", "REST APIs"]


def test_compare_skills_finds_matches_and_gaps() -> None:
    resume = "Python, SQL, Git, teamwork"
    job = "We need Python, SQL, Docker, Git, and communication skills."

    result = compare_skills(resume, job)

    assert result.matched_skills == ["Git", "Python", "SQL"]
    assert result.missing_skills == ["Communication", "Docker"]
    assert result.match_percentage == 60.0


def test_compare_skills_handles_job_with_no_catalog_skills() -> None:
    result = compare_skills("Python", "Curious student wanted")

    assert result.job_skills == []
    assert result.match_percentage == 0.0


def test_skill_evidence_returns_resume_source_text() -> None:
    resume = """
    PROJECTS
    - Built a Flask API with Python and PostgreSQL for 40 students.
    - Used GitHub Actions to run unit tests.
    """

    evidence = extract_skill_evidence(resume)

    assert evidence["Python"] == [
        "Built a Flask API with Python and PostgreSQL for 40 students."
    ]
    assert "GitHub Actions" in evidence["Git"][0]


def test_job_skills_are_split_into_required_and_preferred() -> None:
    job = """
    Requirements:
    - Python, SQL, Git, and communication
    Preferred qualifications:
    - Docker and AWS are a plus
    """

    required, preferred = classify_job_skills(job)

    assert required == ["Communication", "Git", "Python", "SQL"]
    assert preferred == ["AWS", "Docker"]


def test_required_classification_wins_over_preferred_duplicate() -> None:
    job = """
    Preferred qualifications:
    - Python and Docker
    Requirements:
    - Python and SQL
    """

    required, preferred = classify_job_skills(job)

    assert "Python" in required
    assert "Python" not in preferred


def test_comparison_includes_evidence_and_required_score() -> None:
    resume = "Built a Python service and used Git for version control."
    job = "Requirements:\n- Python, Git, SQL\nPreferred:\n- Docker"

    result = compare_skills(resume, job)

    assert result.required_match_percentage == 66.7
    assert result.matched_evidence["Python"] == [
        "Built a Python service and used Git for version control."
    ]
