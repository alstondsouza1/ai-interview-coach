"""Tests for mock-interview selection and performance analytics."""

from src.models import (
    AnswerFeedback,
    MockInterviewAnswer,
    QuestionCategory,
    SkillMatch,
)
from src.mock_interview import (
    MOCK_QUESTION_TOTAL,
    generate_mock_questions,
    readiness_label,
    summarize_mock_interview,
)


def test_mock_interview_has_exact_category_balance() -> None:
    match = SkillMatch(
        resume_skills=["Python", "Git"],
        job_skills=["Python", "Git", "Docker", "Testing"],
        required_skills=["Python", "Git", "Docker", "Testing"],
        matched_skills=["Python", "Git"],
        missing_skills=["Docker", "Testing"],
    )

    questions = generate_mock_questions(match)

    assert len(questions) == MOCK_QUESTION_TOTAL
    assert sum(q.category == QuestionCategory.TECHNICAL for q in questions) == 4
    assert sum(q.category == QuestionCategory.BEHAVIORAL for q in questions) == 3
    assert sum(q.category == QuestionCategory.SITUATIONAL for q in questions) == 3
    assert any("Docker" in question.question for question in questions)


def test_summary_calculates_category_and_rubric_averages() -> None:
    questions = generate_mock_questions(SkillMatch())
    answers = [
        _answer(0, questions[0], 80, 90, 60),
        _answer(1, questions[1], 60, 70, 40),
        _answer(4, questions[4], 70, 80, 50),
    ]

    summary = summarize_mock_interview(answers)

    assert summary.overall_score == 70
    assert summary.category_scores["Technical"] == 70
    assert summary.category_scores["Behavioral"] == 70
    assert summary.category_scores["Situational"] == 0
    assert summary.rubric_scores["Structure"] == 80
    assert summary.average_time_seconds == 50
    assert summary.readiness_label == "In progress"


def test_completed_high_score_is_interview_ready() -> None:
    questions = generate_mock_questions(SkillMatch())
    answers = [
        _answer(index, question, 85, 90, 75)
        for index, question in enumerate(questions)
    ]

    summary = summarize_mock_interview(answers)

    assert summary.readiness_label == "Interview ready"
    assert summary.completed_questions == 10


def test_empty_summary_is_safe() -> None:
    summary = summarize_mock_interview([])

    assert summary.overall_score == 0
    assert summary.readiness_label == "Not started"
    assert summary.category_scores == {
        "Technical": 0,
        "Behavioral": 0,
        "Situational": 0,
    }


def test_readiness_thresholds_require_completion() -> None:
    assert readiness_label(95, 9, 10) == "In progress"
    assert readiness_label(70, 10, 10) == "Nearly ready"
    assert readiness_label(55, 10, 10) == "Developing"


def _answer(
    index: int,
    question,
    score: int,
    structure: int,
    time_taken: int,
) -> MockInterviewAnswer:
    return MockInterviewAnswer(
        question_index=index,
        question=question,
        answer="A sufficiently detailed practice answer for testing.",
        feedback=AnswerFeedback(
            score=score,
            rubric_scores={
                "Structure": structure,
                "Specificity": score,
                "Ownership": score,
                "Impact": score,
                "Clarity": score,
            },
            strengths=["Structure is working well (80/100)."],
            weaknesses=["Impact needs more evidence (50/100)."],
            recommendations=["Add a result."],
            improved_answer="Use a clear structure.",
            summary="Test feedback.",
            word_count=80,
        ),
        time_taken_seconds=time_taken,
    )
