"""Tests for resume, job, plan, and report analysis."""

from src.job_analysis import analyze_job_description
from src.models import (
    AnswerFeedback,
    InterviewQuestion,
    QuestionCategory,
    SkillMatch,
)
from src.preparation_plan import build_preparation_plan
from src.resume_analysis import analyze_resume
from src.session_report import build_markdown_report


def test_resume_analysis_rewards_sections_and_quantified_bullets() -> None:
    resume = """
    EDUCATION
    B.S. Computer Science
    SKILLS
    Python, SQL, Git
    PROJECTS
    - Built an API used by 40 students.
    - Implemented 12 unit tests and improved reliability.
    EXPERIENCE
    - Collaborated with a team of four developers.
    """

    result = analyze_resume(resume)

    assert result.detected_sections == ["Education", "Skills", "Projects", "Experience"]
    assert result.quantified_bullet_count == 2
    assert result.score >= 60


def test_job_analysis_detects_internship_role_and_emphasis() -> None:
    job = """
    Frontend Engineering Intern
    Build React applications, test features, and collaborate with the product team.
    Strong communication and JavaScript skills are required.
    """

    result = analyze_job_description(job)

    assert result.role_family == "Frontend"
    assert result.seniority == "Internship"
    assert "Testing and quality" in result.emphasis_areas


def test_preparation_plan_prioritizes_first_skill_gap() -> None:
    match = SkillMatch(matched_skills=["Python"], missing_skills=["Docker"])
    role = analyze_job_description("Software Engineering Intern")

    plan = build_preparation_plan(match, role)

    assert len(plan) == 7
    assert "Docker" in plan[1].title


def test_report_contains_scores_questions_and_plan() -> None:
    match = SkillMatch(
        matched_skills=["Python"],
        missing_skills=["Docker"],
        match_percentage=50,
    )
    role = analyze_job_description("Software Engineering Intern")
    resume = analyze_resume("EDUCATION\nSKILLS\nPROJECTS\nEXPERIENCE")
    question = InterviewQuestion(
        QuestionCategory.TECHNICAL,
        "Explain a Python project.",
        "Python",
        "Checks project depth.",
    )
    feedback = AnswerFeedback(
        score=72,
        rubric_scores={"Structure": 70},
        strengths=["Clear example."],
        weaknesses=["Needs a result."],
        recommendations=["Add a measured result."],
        improved_answer="Use a problem, action, result structure.",
        summary="Good foundation.",
        word_count=90,
    )
    plan = build_preparation_plan(match, role)

    report = build_markdown_report(
        role, match, resume, [question], {0: feedback}, plan
    )

    assert "# Interview Preparation Report" in report
    assert "**Practice score:** 72/100" in report
    assert "Day 7" in report
