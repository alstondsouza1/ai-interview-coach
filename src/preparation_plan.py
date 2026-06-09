"""Create a focused seven-day interview preparation plan."""

from __future__ import annotations

from src.models import PreparationTask, RoleProfile, SkillMatch


def build_preparation_plan(
    skill_match: SkillMatch, role_profile: RoleProfile
) -> list[PreparationTask]:
    """Create seven practical tasks based on the role and skill gaps."""

    required_gaps = [
        skill
        for skill in skill_match.missing_skills
        if skill in skill_match.required_skills
    ]
    gaps = (
        required_gaps
        or skill_match.missing_skills
        or ["the role's core technical stack"]
    )
    strengths = skill_match.matched_skills or ["your strongest project"]
    return [
        PreparationTask(
            1,
            "Build your introduction",
            f"Write a 60-second introduction connecting your background to {role_profile.detected_title}.",
            30,
            "Story",
        ),
        PreparationTask(
            2,
            f"Review {gaps[0]}",
            f"Learn the fundamentals of {gaps[0]} and write three interview-ready notes.",
            45,
            "Technical",
        ),
        PreparationTask(
            3,
            f"Prepare a {strengths[0]} project story",
            "Practice explaining the problem, your decisions, one tradeoff, and the result.",
            40,
            "Technical",
        ),
        PreparationTask(
            4,
            "Build three STAR stories",
            "Prepare examples for teamwork, a mistake, and learning something quickly.",
            45,
            "Behavioral",
        ),
        PreparationTask(
            5,
            "Practice role fundamentals",
            f"Review common {role_profile.role_family.lower()} concepts and answer two questions aloud.",
            50,
            "Technical",
        ),
        PreparationTask(
            6,
            "Run a timed mock interview",
            "Answer six questions in 30 minutes. Keep each response under two minutes.",
            45,
            "Practice",
        ),
        PreparationTask(
            7,
            "Polish and prepare questions",
            "Review weak answers and prepare five thoughtful questions for the interviewer.",
            35,
            "Final review",
        ),
    ]
