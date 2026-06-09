"""Generate personalized interview questions from resume and job context."""

from __future__ import annotations

import json

from src.ai_client import AIClient, AIServiceError
from src.models import InterviewQuestion, QuestionCategory, SkillMatch

QUESTION_COUNT = 6


def generate_questions(
    resume_text: str,
    job_description: str,
    skill_match: SkillMatch,
    ai_client: AIClient | None = None,
) -> tuple[list[InterviewQuestion], str | None]:
    """Generate six questions, using a local fallback if AI is unavailable.

    Returns:
        A question list and an optional warning explaining why fallback mode ran.
    """

    if ai_client is not None:
        try:
            data = ai_client.complete_json(
                _question_system_prompt(),
                _question_user_prompt(resume_text, job_description, skill_match),
            )
            return _parse_questions(data), None
        except (AIServiceError, KeyError, TypeError, ValueError) as exc:
            return _fallback_questions(skill_match), str(exc)

    return _fallback_questions(skill_match), None


def _question_system_prompt() -> str:
    return """
You are an interview coach for students applying to internships and entry-level
software engineering roles. Create practical questions at an appropriate
difficulty. Return valid JSON only with a "questions" array. Every item must
have "category", "question", "focus_area", and "why_asked". Generate exactly
six items: two Technical, two Behavioral, and two Situational. Do not invent
resume experience. Keep each question focused on one topic.
""".strip()


def _question_user_prompt(
    resume_text: str, job_description: str, skill_match: SkillMatch
) -> str:
    context = {
        "resume": resume_text[:8000],
        "job_description": job_description[:6000],
        "matched_skills": skill_match.matched_skills,
        "missing_skills": skill_match.missing_skills,
    }
    return "Create a personalized practice interview from this context:\n" + json.dumps(
        context
    )


def _parse_questions(data: dict) -> list[InterviewQuestion]:
    raw_questions = data["questions"]
    if not isinstance(raw_questions, list) or len(raw_questions) != QUESTION_COUNT:
        raise ValueError("The AI response did not contain exactly six questions.")

    questions = [
        InterviewQuestion(
            category=QuestionCategory(item["category"].title()),
            question=str(item["question"]).strip(),
            focus_area=str(item["focus_area"]).strip(),
            why_asked=str(item["why_asked"]).strip(),
        )
        for item in raw_questions
    ]
    category_counts = {
        category: sum(question.category == category for question in questions)
        for category in QuestionCategory
    }
    if any(count != 2 for count in category_counts.values()):
        raise ValueError("The AI response did not include two questions per category.")
    if any(not question.question for question in questions):
        raise ValueError("The AI response included an empty question.")
    return questions


def _fallback_questions(skill_match: SkillMatch) -> list[InterviewQuestion]:
    """Create useful questions without sending data to an external service."""

    strongest = _first_or_default(skill_match.matched_skills, "a project you built")
    second_skill = _first_or_default(skill_match.matched_skills[1:], strongest)
    gap = _first_or_default(skill_match.missing_skills, "a new technology")

    return [
        InterviewQuestion(
            QuestionCategory.TECHNICAL,
            f"Explain how you used {strongest} in a project. What problem did it solve?",
            strongest,
            "Checks whether you can connect a listed skill to hands-on experience.",
        ),
        InterviewQuestion(
            QuestionCategory.TECHNICAL,
            f"How would you test and debug a feature built with {second_skill}?",
            second_skill,
            "Tests your development process and attention to software quality.",
        ),
        InterviewQuestion(
            QuestionCategory.BEHAVIORAL,
            "Tell me about a time you received difficult feedback on your work.",
            "Growth mindset",
            "Entry-level teams value students who can learn from feedback.",
        ),
        InterviewQuestion(
            QuestionCategory.BEHAVIORAL,
            "Describe a team project where you disagreed with another person. What did you do?",
            "Teamwork",
            "Explores communication, listening, and conflict resolution.",
        ),
        InterviewQuestion(
            QuestionCategory.SITUATIONAL,
            f"You need to use {gap} but have never used it before. How would you get started?",
            gap,
            "Evaluates how you learn a skill that appears in the job requirements.",
        ),
        InterviewQuestion(
            QuestionCategory.SITUATIONAL,
            "A task is taking longer than expected and the deadline is tomorrow. What do you do?",
            "Prioritization",
            "Checks communication, planning, and ownership under pressure.",
        ),
    ]


def _first_or_default(items: list[str], default: str) -> str:
    return items[0] if items else default

