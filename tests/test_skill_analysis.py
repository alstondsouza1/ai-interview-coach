"""Tests for deterministic skill extraction and matching."""

from src.skill_analysis import compare_skills, extract_skills


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

