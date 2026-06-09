"""Tests for local question generation and transparent answer evaluation."""

import pytest

from src.answer_evaluator import evaluate_answer
from src.models import InterviewQuestion, QuestionCategory, SkillMatch
from src.question_generator import generate_questions


def test_generator_creates_two_questions_per_category() -> None:
    match = SkillMatch(
        matched_skills=["Python", "Git"],
        missing_skills=["Docker"],
    )

    questions = generate_questions("", "", match)

    assert len(questions) == 6
    assert [question.category for question in questions].count(
        QuestionCategory.TECHNICAL
    ) == 2
    assert any("Docker" in question.question for question in questions)


def test_short_answer_is_rejected() -> None:
    question = InterviewQuestion(
        QuestionCategory.BEHAVIORAL, "Tell me about a project.", "Teamwork", "Reason"
    )

    with pytest.raises(ValueError, match="complete sentences"):
        evaluate_answer(question, "It went well.", "")


def test_detailed_answer_scores_better_than_generic_answer() -> None:
    question = InterviewQuestion(
        QuestionCategory.BEHAVIORAL, "Tell me about a project.", "Teamwork", "Reason"
    )
    generic = (
        "Our team worked on a class project together and we completed the assigned work. "
        "We communicated with each other and submitted it before the deadline."
    )
    detailed = (
        "During a class project, our API was failing before the demo. I tested each "
        "endpoint, found an incorrect database query, and implemented the fix. For "
        "example, I also added three regression tests. The result was a successful "
        "demo, and I learned to add tests earlier in the project."
    )

    generic_feedback = evaluate_answer(question, generic)
    detailed_feedback = evaluate_answer(question, detailed)

    assert detailed_feedback.score > generic_feedback.score
    assert (
        detailed_feedback.rubric_scores["Specificity"]
        > generic_feedback.rubric_scores["Specificity"]
    )
