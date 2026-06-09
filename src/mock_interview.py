"""Timed mock-interview question selection and performance analytics."""

from __future__ import annotations

from collections import Counter, defaultdict

from src.answer_evaluator import RUBRIC_WEIGHTS
from src.models import (
    InterviewQuestion,
    MockInterviewAnswer,
    MockInterviewSummary,
    QuestionCategory,
    SkillMatch,
)
from src.question_generator import QUESTION_BANK, _best_template_skill, _question_priority

MOCK_QUESTION_COUNTS = {
    QuestionCategory.TECHNICAL: 4,
    QuestionCategory.BEHAVIORAL: 3,
    QuestionCategory.SITUATIONAL: 3,
}
MOCK_QUESTION_TOTAL = sum(MOCK_QUESTION_COUNTS.values())


def generate_mock_questions(skill_match: SkillMatch) -> list[InterviewQuestion]:
    """Create a balanced 10-question interview from the local question bank."""

    relevant_skills = set(skill_match.job_skills) | set(skill_match.resume_skills)
    missing_skills = set(skill_match.missing_skills)
    required_gaps = missing_skills & set(skill_match.required_skills)
    ordered_gaps = [
        *[
            skill
            for skill in skill_match.missing_skills
            if skill in skill_match.required_skills
        ],
        *[
            skill
            for skill in skill_match.missing_skills
            if skill not in skill_match.required_skills
        ],
    ]
    questions: list[InterviewQuestion] = []

    for category, count in MOCK_QUESTION_COUNTS.items():
        ranked = sorted(
            QUESTION_BANK[category],
            key=lambda item: _question_priority(
                item["skills"], relevant_skills, missing_skills, required_gaps
            ),
            reverse=True,
        )
        for item in ranked[:count]:
            template_skill = _best_template_skill(
                item["skills"], ordered_gaps, skill_match.matched_skills
            )
            questions.append(
                InterviewQuestion(
                    category=category,
                    question=str(item["question"]).format(skill=template_skill),
                    focus_area=str(item["focus"]).format(skill=template_skill),
                    why_asked=str(item["why"]),
                )
            )

    if len(questions) != MOCK_QUESTION_TOTAL:
        raise ValueError("The question bank cannot build a complete mock interview.")
    return questions


def summarize_mock_interview(
    answers: list[MockInterviewAnswer],
    total_questions: int = MOCK_QUESTION_TOTAL,
) -> MockInterviewSummary:
    """Aggregate answer feedback into category, rubric, and readiness results."""

    if not answers:
        return MockInterviewSummary(
            overall_score=0,
            readiness_label="Not started",
            category_scores={category.value: 0 for category in QuestionCategory},
            rubric_scores={name: 0 for name in RUBRIC_WEIGHTS},
            strengths=[],
            weaknesses=["Complete at least one question to receive feedback."],
            completed_questions=0,
            total_questions=total_questions,
            average_time_seconds=0,
        )

    category_values: dict[str, list[int]] = defaultdict(list)
    rubric_values: dict[str, list[int]] = defaultdict(list)
    strength_counter: Counter[str] = Counter()
    weakness_counter: Counter[str] = Counter()

    for item in answers:
        category_values[item.question.category.value].append(item.feedback.score)
        for rubric, score in item.feedback.rubric_scores.items():
            rubric_values[rubric].append(score)
        strength_counter.update(_feedback_areas(item.feedback.strengths))
        weakness_counter.update(_feedback_areas(item.feedback.weaknesses))

    category_scores = {
        category.value: _average(category_values[category.value])
        for category in QuestionCategory
    }
    rubric_scores = {
        rubric: _average(rubric_values[rubric]) for rubric in RUBRIC_WEIGHTS
    }
    overall_score = round(
        sum(answer.feedback.score for answer in answers) / len(answers)
    )

    return MockInterviewSummary(
        overall_score=overall_score,
        readiness_label=readiness_label(overall_score, len(answers), total_questions),
        category_scores=category_scores,
        rubric_scores=rubric_scores,
        strengths=_ranked_areas(strength_counter, "Consistently strong"),
        weaknesses=_ranked_areas(weakness_counter, "Needs the most attention"),
        completed_questions=len(answers),
        total_questions=total_questions,
        average_time_seconds=round(
            sum(answer.time_taken_seconds for answer in answers) / len(answers)
        ),
    )


def readiness_label(score: int, completed: int, total: int) -> str:
    """Return a conservative readiness label based on score and completion."""

    if completed < total:
        return "In progress"
    if score >= 82:
        return "Interview ready"
    if score >= 68:
        return "Nearly ready"
    if score >= 52:
        return "Developing"
    return "Needs focused practice"


def timer_status(
    started_at: float, duration_seconds: int, current_time: float
) -> tuple[int, int, bool]:
    """Return elapsed seconds, remaining seconds, and timeout status."""

    elapsed = max(0, int(current_time - started_at))
    remaining = max(0, duration_seconds - elapsed)
    return elapsed, remaining, elapsed >= duration_seconds


def _feedback_areas(items: list[str]) -> list[str]:
    areas = []
    for item in items:
        area = item.split(" ", 1)[0].strip(".,:")
        if area in RUBRIC_WEIGHTS:
            areas.append(area)
    return areas


def _ranked_areas(counter: Counter[str], prefix: str) -> list[str]:
    return [f"{prefix}: {area}." for area, _ in counter.most_common(3)]


def _average(values: list[int]) -> int:
    return round(sum(values) / len(values)) if values else 0
